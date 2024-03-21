import os
import subprocess

def newBridge(bridgename):
    os.system("brctl addbr "+bridgename)
    os.system("sudo ip link set up "+bridgename)
    t = subprocess.check_output("ip link show "+bridgename, shell=True)
    if "UP" in str(t):
        print("Bridge", bridgename, "created")

def showBridges(bridgename):
    os.system("sudo brctl show | grep "+bridgename)

def rmBridge(bridgename):
    os.system("sudo ip link set down "+bridgename)
    os.system("brctl delbr "+bridgename)

def isRunning(bridgename):
    t = subprocess.check_output("sudo brctl show", shell=True)
    if bridgename in str(t):
        return True
    else:
        return False

