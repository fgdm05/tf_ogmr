import sys
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

gateway = '10.90.90.90'

async def walk_table(mib_name="BRIDGE-MIB", table_name="dot1dTpFdbTable", gateway="10.90.90.90", community="public", port=161):
    snmpEngine = SnmpEngine()
    if mib_name:
        initial_object = ObjectType(ObjectIdentity(mib_name, table_name))
    else:
        initial_object = ObjectType(ObjectIdentity(table_name))

    
    # Cria o transport target adequadamente
    transport_target = await UdpTransportTarget.create((gateway, port))
    
    # loop para caminhar (walk) pela tabela
    # next_cmd retorna um gerador assíncrono no PySNMP moderno
    iterator = await next_cmd(
        snmpEngine,
        CommunityData(community, mpModel=0),  # mpModel=0 significa SNMPv1, mPModel=1 para v2c
        transport_target,
        ContextData(),
        initial_object
    )

    print(f"--- Buscando tabela {mib_name}::{table_name} de {gateway} ---")

    async for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            print(f"Erro de Indicação: {errorIndication}")
            break
        elif errorStatus:
            print(f"Erro de Status: {errorStatus.prettyPrint()} em {errorIndex}")
            break
        else:
            for varBind in varBinds:
                # Verificação crítica: Garante que o SNMP não continue andando infinitamente
                # por outras MIBs do switch após o fim da tabela desejada.
                if not initial_object[0].isPrefixOf(varBind[0]):
                    # Se o OID retornado não começar mais com o OID da nossa tabela, terminamos.
                    snmpEngine.close_dispatcher()
                    return

                # Exibe o resultado (Ex: dot1dTpFdbPort.0.33.112.161.42.11 = 5)
                print(" = ".join([x.prettyPrint() for x in varBind]))

    snmpEngine.close_dispatcher()


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


async def set_port(port, vlan):
    errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
        SnmpEngine(),
        CommunityData('private', mpModel=0),
        await UdpTransportTarget.create(('10.90.90.90', 161)),
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
    descrs = await snmp_walk(
        'public',
        "1.3.6.1.2.1.2.2.1.2"
    )

    admins = await snmp_walk(
        'public',
        "1.3.6.1.2.1.2.2.1.7"
    )

    opers = await snmp_walk(
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

def interface():
    sgateway = "10.90.90.90"
    subnet_mask = "255.0.0.0"
    while (1):
        print(f"[1] Listar todas as portas + IPs + &MACs + nome dispositivo")
        print(f"[2] Bloquear porta")
        print(f"[3] Desbloquear porta")
        print(f"[4] Desbloquear todas as portas")
        print(f"[5] Listar estados das portas")
        print(f"[0] Sair")
        val = int(input(""))
        if(val == 1):
            asyncio.run(walk_table(
                mib_name=None,
                table_name=".1.3.6.1.2.1.17.4.3",
                gateway=sgateway,
                community="public"
            ))
            
            
        elif(val == 2):
            port = input(f"Bloquear qual porta? ")
            asyncio.run(set_port(port, 2))
        elif(val == 3):
            port = input(f"Desbloquear qual porta? ")
            asyncio.run(set_port(port, 1))
        elif(val == 5):
            
            ports = asyncio.run(inter())

            for p in ports:
                print(
                    f"{p['ifindex']:3d} "
                    f"{p['name']:30s} "
                    f"admin={p['admin']:5s} "
                    f"oper={p['oper']}"
                )
    
        elif(val == 0):
            print("Finalizando programa")
            exit(0)        
        else:
            print(f"Opção {val} inválida.")
def main(args):
    
    interface()

if __name__ == "__main__":
    main(sys.argv[1:])