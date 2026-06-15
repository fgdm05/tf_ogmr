from pysnmp.hlapi import *

# Target device details
HOST = '10.90.90.90'
COMMUNITY = 'public'

# OID for the MAC address column
mac_oid = ObjectType(ObjectIdentity('BRIDGE-MIB', 'dot1dTpFdbAddress'))
# OID for the port ID column
port_oid = ObjectType(ObjectIdentity('BRIDGE-MIB', 'dot1dTpFdbPort'))

# Create SNMP engine and transport target
snmp_engine = SnmpEngine()
transport_target = UdpTransportTarget((HOST, 161))
community_data = CommunityData(COMMUNITY)
context_data = ContextData()

# Execute bulk walk
for (errorIndication, errorStatus, errorIndex, varBindTable) in bulkCmd(
    snmp_engine,
    community_data,
    transport_target,
    context_data,
    0, 25,  # non-repeaters, max-repetitions
    mac_oid,
    port_oid,
    lexicographicMode=False
):
    if errorIndication:
        print(f'Error: {errorIndication}')
    elif errorStatus:
        print(f'Error Status: {errorStatus.prettyPrint()} at {errorIndex}')
    else:
        # varBindTable is a list of rows; each row is a list of varBinds
        for varBinds in varBindTable:
            mac_addr = None
            port_id = None
            for varBind in varBinds:
                if 'dot1dTpFdbAddress' in varBind[0].prettyPrint():
                    mac_addr = varBind[1].prettyPrint()
                elif 'dot1dTpFdbPort' in varBind[0].prettyPrint():
                    port_id = varBind[1].prettyPrint()
            
            if mac_addr and port_id:
                print(f'MAC: {mac_addr} -> Port: {port_id}')   