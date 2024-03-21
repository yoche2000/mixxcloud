#input: tenantID, vpcID, subnetID ,CIDR

import bridge
import util_ip
import libnet
import os
import argparse

p = argparse.ArgumentParser()

p.add_argument("-t", "--tenantID", type=str,
        help="tenantID")
p.add_argument("-v", "--vpcID", type=str,
        help="vpcID")
p.add_argument("-s", "--subnetID", type=str,
        help="subnetID, auto generate if not assigned.")
p.add_argument("-c", "--cidr", type=str,
        help="CIDR, e.g., 192.168.1.0/24")
args = p.parse_args()

if args.tenantID:
    tenantID = args.tenantID
else:
    exit("tenantID missing.")
if args.vpcID:
    vpcID = args.vpcID
else:
    exit("vpcID missing")
if args.subnetID:
    subnetID = args.subnetID
else:
    exit("subnetID missing")
if args.cidr:
    cidr = args.cidr
else:
    exit("cidr missing")


'''
verify input
'''

try:
    print("Input:", tenantID, vpcID, subnetID, cidr)
except NameError:
    exit("One of the required parameter was not included.")

## check is CIDR is in the correct format
try:
    n_cidr= util_ip.check_subnet(cidr)
except ValueError:
    exit("CIDR error")

## if tenantID exist -> yes
## if vpcID under tenantID -> yes
## if subneID in vpcID -> no
## if CIDR in vpc range and unused


'''
Verifying subnet
'''
## check subnet for colision




'''
Verify Router is running
'''
routeID = "RT_"+ tenantID + "_" + subnetID
## verify router VM running
## vmRunning(routerID)



'''
Creating Bridge using bridge.py
'''
bridgeID = "BR_" + tenantID + "_" + subnetID
if bridge.isRunning(bridgeID):
    print("Bridge", bridgeID, "exists.")
else:
    bridge.newBridge(bridgeID)
    print("Bridge created, bridgeID:", bridgeID)

'''
## rollback
'''
## bridge.rmBridge(bridgeID)




'''
networkID = createNetwork(bridgeID, CIDR)
'''

networkID = "NW_" + tenantID + "_" + subnetID
if libnet.isRunning(networkID):
    print("Network", bridgeID, "exists.")
else:
    libnet.newNet(networkID, bridgeID, n_cidr)

'''
rollback
'''
## libnet.rmNet(networkID)


'''
attachSubnettoRouter(routerID, networkID)
'''






'''
Append entries in db
'''
