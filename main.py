import sys
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
import uuid
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
        ObjectType(ObjectIdentity(local, OID, 0)),
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
    transport = await UdpTransportTarget.create((gateway, 161))

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

async def inter():
    descrs = await snmp_walk_raw(
        'public',
        "1.3.6.1.2.1.2.2.1.2"
    )
    
    admins = await snmp_walk_raw(
        'public',
        "1.3.6.1.2.1.2.2.1.7"
    )

    opers = await snmp_walk_raw(
        'public',
        "1.3.6.1.2.1.2.2.1.8"
    )

    interfaces = []

    for idx in sorted(descrs.keys()):
        interfaces.append({
            "ifindex": idx,
            "name": str(descrs.get(idx, "")),
            "admin": STATUS.get(int(admins.get(idx, 0)), "unknown"),
            "oper": STATUS.get(int(opers.get(idx, 0)), "unknown")
        })
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
    ports = await inter()
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
            ports = asyncio.run(inter())

            for p in ports:
                print(
                    f"{p['ifindex']:3d} "
                    f"{p['name']:30s} "
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