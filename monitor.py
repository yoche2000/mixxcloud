import os
import subprocess

## A set of functions to check the state of bridges/networks/vms

def verifyBridge(bridgename):
    output = subprocess.check_output("sudo brctl show", shell=True)
    if bridgename in str(output):
        return True
    return False

def verifyNet(networkID):
    output = subprocess.check_output("sudo virsh net-list --all", shell=True)
    if networkID in str(output):
        state = subprocess.check_output("sudo virsh net-list --all | grep "+networkID, shell=True)
        if "inactive" in str(state):
            return "defined"        #stopped
        else:
            return "started"        #started
    return False                    #Undefined

def verifyVM(vmName):
    output = subprocess.check_output("sudo virsh list --all", shell=True)
    if vmName in str(output):
        state = subprocess.check_output("sudo virsh list --all | grep "+ vmName, shell=True)
        if "running" in str(state):
            return "running"        #stopped
        else:
            return "shutoff"        #started
    return False                    #Undefined


print(verifyVM('14-Guest-VM2'))
print(verifyVM('14-Guest-VM3'))
print(verifyVM('14-Guest-VM4'))

