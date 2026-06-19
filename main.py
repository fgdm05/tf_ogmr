import sys
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
import uuid
from itertools import groupby
#gateway = "10.204.132.51"
gateway = '10.90.90.90'



mac = ':'.join(
    f'{(uuid.getnode() >> i) & 0xff:02x}'
    for i in range(40, -1, -8)
).lower()

print(mac)

async def run(OID = "sysDescr", local = "SNMPv2-MIB", gateway = "demo.pysnmp.com", community = "public", port = 161):
    snmpEngine = SnmpEngine()

    iterator = get_cmd(
        snmpEngine,
        CommunityData(community, mpModel=0),
        await UdpTransportTarget.create((gateway, port)),
        ContextData(),
        ObjectType(ObjectIdentity(OID)),
    )

    errorIndication, errorStatus, errorIndex, varBinds = await iterator

    if errorIndication:
        print(errorIndication)

    elif errorStatus:
        print(
            "{} at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )
    else:
        for varBind in varBinds:
            print(" = ".join([x.prettyPrint() for x in varBind]))


    snmpEngine.close_dispatcher()
    return varBinds

# snmpwalk -v1 -c private 10.90.90.90
# snmpwalk -v1 -c public 10.90.90.90 dot1dTpFdbTable
# snmpwalk -v1 -c public 10.90.90.90 ifIndex
# snmpwalk -v1 -c public 10.90.90.90 ipAddrTable
#

STATUS = {
    1: "up",
    2: "down",
    3: "testing",
    4: "unknown",
    5: "dormant",
    6: "notPresent",
    7: "lowerLayerDown"
}
async def snmp_walk(community, oid):
    transport = await UdpTransportTarget.create((gateway, 161))

    result = {}

    async for errorIndication, errorStatus, errorIndex, varBinds in walk_cmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),  # SNMPv2c
        transport,
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    ):
        if errorIndication:
            raise RuntimeError(errorIndication)

        if errorStatus:
            raise RuntimeError(
                f"{errorStatus.prettyPrint()} at {errorIndex}"
            )

        for oid_obj, value in varBinds:
            idx = int(str(oid_obj).split('.')[-1])
            result[idx] = value

    return result


async def snmp_walk_raw(community, oid):
    transport = await UdpTransportTarget.create((gateway, 161), timeout=5.0)

    result = []

    async for errorIndication, errorStatus, errorIndex, varBinds in walk_cmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        transport,
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    ):
        if errorIndication:
            raise RuntimeError(errorIndication)

        if errorStatus:
            raise RuntimeError(
                f"{errorStatus.prettyPrint()} at {errorIndex}"
            )

        for oid_obj, value in varBinds:
            result.append((str(oid_obj), value))

    return result

STATUS_MAP = {
    '1': 'Up (Ligada)', '2': 'Down (Desligada)', '3': 'Testing',
    '4': 'Unknown', '5': 'Dormant', '6': 'NotPresent', '7': 'LowerLayerDown'
}

# Funções auxiliares rápidas para formatar e limpar os MAC Addresses
def limpar_mac_arp(val):
    m = val.prettyPrint()[2:] if val.prettyPrint().startswith("0x") else val.prettyPrint()
    return ":".join(m[i:i+2] for i in range(0, len(m), 2)).upper()

def extrair_mac_oid(oid_str):
    return ":".join(f"{int(x):02x}" for x in oid_str.split('.')[-6:]).upper()


async def mapear_todas_as_portas():
    print("[INFO] Disparando todos os SNMP WALKs em paralelo...")
    
    community="public"
    resultados = await asyncio.gather(
        snmp_walk_raw(community, "1.3.6.1.2.1.2.2.1.2"),    # 0: Nomes (ifDescr)
        snmp_walk_raw(community, "1.3.6.1.2.1.2.2.1.7"),    # 1: AdminStatus
        snmp_walk_raw(community, "1.3.6.1.2.1.2.2.1.8"),    # 2: OperStatus
        snmp_walk_raw(community, "1.3.6.1.2.1.4.22.1.2"),   # 3: ARP Table (IP -> MAC)
        snmp_walk_raw(community, "1.3.6.1.2.1.17.1.4.1.2"), # 4: Bridge Port -> ifIndex
        snmp_walk_raw(community, "1.3.6.1.2.1.17.4.3.1.2"), # 5: MAC -> Bridge Port
        return_exceptions=True
    )
    
    
    w_nomes  = resultados[0] if not isinstance(resultados[0], Exception) else []
    w_admin  = resultados[1] if not isinstance(resultados[1], Exception) else []
    w_oper   = resultados[2] if not isinstance(resultados[2], Exception) else []
    w_arp    = resultados[3] if not isinstance(resultados[3], Exception) else []
    w_bridge = resultados[4] if not isinstance(resultados[4], Exception) else []
    w_macs   = resultados[5] if not isinstance(resultados[5], Exception) else []

    
    admin_map  = {oid.split('.')[-1]: STATUS_MAP.get(str(val), str(val)) for oid, val in w_admin}
    oper_map   = {oid.split('.')[-1]: STATUS_MAP.get(str(val), str(val)) for oid, val in w_oper}
    bridge_map = {oid.split('.')[-1]: str(val) for oid, val in w_bridge}
    arp_map    = {limpar_mac_arp(val): ".".join(oid.split('.')[-4:]) for oid, val in w_arp}

    
    mac_list_ordenada = sorted(
        [
            (bridge_map.get(str(val)), extrair_mac_oid(oid), arp_map.get(extrair_mac_oid(oid), "Desconhecido"))
            for oid, val in w_macs if bridge_map.get(str(val))
        ],
        key=lambda x: x[0]
    )
    mac_grouped = {k: [{'mac': m, 'ip': i} for _, m, i in g] for k, g in groupby(mac_list_ordenada, key=lambda x: x[0])}

    
    portas = {}
    for oid, val in w_nomes:
        ifindex = oid.split('.')[-1]
        portas[ifindex] = {
            'ifindex': ifindex,
            'nome': str(val),
            'admin_status': admin_map.get(ifindex, 'Desconhecido'),
            'oper_status': oper_map.get(ifindex, 'Desconhecido'),
            'dispositivos': mac_grouped.get(ifindex, []) 
        }

    return portas


async def set_port(port, vlan):
    errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
        SnmpEngine(),
        CommunityData('private', mpModel=0),
        await UdpTransportTarget.create((gateway, 161)),
        ContextData(),
        ObjectType(
            ObjectIdentity(
                f'1.3.6.1.2.1.2.2.1.7.{port}'
            ),
            Integer(vlan)
        ),
        lookupMib=False
    )

    if errorIndication:
        print("Error:", errorIndication)
    elif errorStatus:
        print(
            f'{errorStatus.prettyPrint()} '
            f'at {errorIndex and varBinds[int(errorIndex)-1][0] or "?"}'
        )
    else:
        print("Success:", varBinds)



import binascii
async def inter(ports):
   

    # --- Helper Functions ---

    def parse_to_dict(snmp_list):
        """Splits '1.3.6.1.2.1.2.2.1.2.5' by '.' and grabs the last element '5' as an int key."""
        return {int(oid.split('.')[-1]): val for oid, val in snmp_list}

    def parse_ip_to_dict(snmp_list):
        """
        IP table (1.3.6.1.2.1.4.20.1.1) returns the IP address in the OID suffix, 
        and the ifIndex as the value. We reverse this to map ifIndex -> IP string.
        """
        ip_map = {}
        for oid, val in snmp_list:
            try:
                # The last 4 digits of the OID form the IP address (e.g., ...20.1.1.192.168.1.1)
                parts = oid.split('.')
                ip_str = ".".join(parts[-4:])
                ifIndex = int(val)
                ip_map[ifIndex] = ip_str
            except (ValueError, IndexError):
                continue
        return ip_map

    def format_mac(raw_mac):
        """Converts raw bytes or octet strings into a standard aa:bb:cc:dd:ee:ff format."""
        if not raw_mac:
            return ""
        # If it's already a string representation, handle it or convert bytes
        if isinstance(raw_mac, bytes):
            hex_str = binascii.hexlify(raw_mac).decode('utf-8')
        else:
            # Fallback for pretty printed / PySNMP native objects
            hex_str = binascii.hexlify(bytes(raw_mac)).decode('utf-8')
            
        if len(hex_str) == 12:
            return ":".join(hex_str[i:i+2] for i in range(0, 12, 2))
        return str(raw_mac) # Fallback if it's an empty or abnormal string


    # --- Main Logic ---

    # 1. Fetch all raw walks asynchronously
    descrs_raw = await snmp_walk_raw('public', "1.3.6.1.2.1.2.2.1.2")  # ifDescr
    admins_raw = await snmp_walk_raw('public', "1.3.6.1.2.1.2.2.1.7")  # ifAdminStatus
    opers_raw  = await snmp_walk_raw('public', "1.3.6.1.2.1.2.2.1.8")  # ifOperStatus
    macs_raw   = await snmp_walk_raw('public', "1.3.6.1.2.1.2.2.1.6")  # ifPhysAddress
    ips_raw    = await snmp_walk_raw('public', "1.3.6.1.2.1.4.20.1.1")  # ipAdEntAddr

    # 2. Convert raw data to standardized lookup dictionaries keyed by ifIndex
    descr_dict = parse_to_dict(descrs_raw)
    admin_dict = parse_to_dict(admins_raw)
    oper_dict  = parse_to_dict(opers_raw)
    mac_dict   = parse_to_dict(macs_raw)
    ip_dict    = parse_ip_to_dict(ips_raw)

    # 3. Combine them by looping through the master interface list
    interfaces = []
    for idx in sorted(descr_dict.keys()):
        if(idx in ports):
            interfaces.append({
                "ifindex": idx,
                "name": str(descr_dict.get(idx, "")),
                "admin": STATUS.get(int(admin_dict.get(idx, 0)), "unknown"),
                "oper": STATUS.get(int(oper_dict.get(idx, 0)), "unknown"),
                "mac": format_mac(mac_dict.get(idx, "")),
                "ip": ip_dict.get(idx, "N/A")  # Uses "N/A" if no IP is bound to this interface
            })
        else: 
            continue
    print("###################################")
    
    return interfaces

async def tabela():
    hosts = []
    interfaces = await inter()
    port_status = {
        p["ifindex"]: {
            "admin": p["admin"],
            "oper": p["oper"]
        }
        for p in interfaces
    }
    arp_entries = await snmp_walk_raw(
        'private',
        "1.3.6.1.2.1.4.22.1.2"
    )
    print(type(arp_entries))
    print(arp_entries)

    for oid, mac in arp_entries:

        parts = oid.split('.')

        # ifIndex.IPv4
        ip = '.'.join(parts[-4:])
        ifIndex = int(parts[-5])

        try:
            mac_addr = ':'.join(
                f'{b:02x}' for b in mac.asOctets()
            )
        except AttributeError:
            mac_addr = str(mac)

        hosts.append({
            "ip": ip,
            "mac": mac_addr,
            "admin": port_status.get(ifIndex, {}).get("admin", "unknown"),
            "oper": port_status.get(ifIndex, {}).get("oper", "unknown")
        })

    for host in hosts:
        print(host)

async def abrirTodas():
    ports = await inter([])
    for port in range(1, 25, 1):
        print(f"Abrindo porta {port}")
        await set_port(port, 1)



async def bloquearTodasExceto(left, right, index):
    ports = await inter()
    for port in range(left, right, 1):
        if port == index:
            print(f'Mantendo porta {index}')
            continue

        print(f"Desabilitando {port}")
        await set_port(port, 2)


def interface():
    while (1):
        print(f"[1] Listar todas as portas + IPs + &MACs + nome dispositivo")
        print(f"[2] Bloquear porta")
        print(f"[3] Desbloquear porta")
        print(f"[4] Desbloquear todas as portas")
        print(f"[5] Listar estados das portas")
        print(f"[6] Fechar todas as portas exceto")
        print(f"[0] Sair")
        val = int(input(""))
        if(val == 1):
            ret = asyncio.run(tabela())
            
        elif(val == 2):
            port = input(f"Bloquear qual porta? ")
            asyncio.run(set_port(port, 2))
        elif(val == 3):
            port = input(f"Desbloquear qual porta? ")
            asyncio.run(set_port(port, 1))
        elif(val == 4):
            asyncio.run(abrirTodas())
        elif(val == 5):
            ports = asyncio.run(inter(list(range(1,25))))

            for p in ports:
                print(
                    f"{p['ifindex']:3d} "
                    f"{p['name']:30s} "
                    f"{p['mac']} "
                    f"{p['ip']} "
                    f"admin={p['admin']:5s} "
                    f"oper={p['oper']}"

                )
        elif(val == 6):

            asyncio.run(bloquearTodasExceto(8,12,9))
        elif(val == 0):
            print("Finalizando programa")
            exit(0)        
        else:
            print(f"Opção {val} inválida.")
def main(args):
    
    interface()

if __name__ == "__main__":
    main(sys.argv[1:])