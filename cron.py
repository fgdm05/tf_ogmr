import sys
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
gateway = "10.90.90.90"

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

def main(argv):
	
	asyncio.run(set_port(argv[0], argv[2]))


if __name__ == "__main__":
	main(sys.argv[1:])

	