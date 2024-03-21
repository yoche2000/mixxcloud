#input: tenantID, vpcID, subnetID ,CIDR

import bridge
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


'''
verify input
'''

try:
    print("Input:", tenantID, vpcID, subnetID)
except NameError:
    exit("One of the required parameter was not included.")


## if tenantID exist -> yes
## if vpcID under tenantID -> yes
## if subneID in vpcID -> yes



'''
detatch router from network
'''
## intDetatch(routerID, networkID)




'''
Remove Libvirt Network
'''

##if network exist, rm, else exit()
networkID = "NW_" + tenantID + "_" + subnetID
if libnet.isRunning(networkID):
    libnet.rmNet(networkID)
    print("Network", networkID, "deleted.")
else:
    print("Network", networkID, 'does not exist.')

# if bridge exist, rm, else exit()
bridgeID = "BR_" + tenantID + "_" + subnetID
if bridge.isRunning(bridgeID):
    bridge.rmBridge(bridgeID)
    print("Bridge", bridgeID, 'deleted.')
else:
    print("Bridge", bridgeID, 'does not exist.')
