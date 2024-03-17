import os
import subprocess

def newBridge(bridgename):
    os.system("brctl addbr "+bridgename)
    os.system("sudo ip link set up "+bridgename)
    os.system("ip link show "+bridgename)   

def showBridges(bridgename):
    os.system("sudo brctl show | grep "+bridgename)

def rmBridge(bridgename):
    os.system("sudo ip link set down "+bridgename)
    os.system("brctl delbr "+bridgename)
