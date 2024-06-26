import os
import subprocess

class SubnetBridge:
    @staticmethod
    def newBridge(bridgename: str):
        SubnetBridge.check_is_not_empty(bridgename)
        os.system("brctl addbr "+bridgename)
        os.system("sudo ip link set up "+bridgename)
        t = subprocess.check_output("ip link show "+bridgename, shell=True)
        if "UP" in str(t):
            print("Bridge", bridgename, "created")

    @staticmethod
    def showBridges(bridgename: str):
        SubnetBridge.check_is_not_empty(bridgename)
        if not bridgename:
            raise Exception("bridgename is required")
        os.system("sudo brctl show | grep "+bridgename)

    @staticmethod
    def rmBridge(bridgename: str):
        SubnetBridge.check_is_not_empty(bridgename)
        os.system("sudo ip link set down "+bridgename)
        os.system("brctl delbr "+bridgename)

    @staticmethod
    def isRunning(bridgename: str):
        SubnetBridge.check_is_not_empty(bridgename)
        t = subprocess.check_output("sudo brctl show", shell=True)
        return bridgename in str(t)
        
    @staticmethod
    def check_is_not_empty(txt):
        if not txt:
            raise Exception("bridgename is required")

if __name__ == '__main__':
    found = SubnetBridge.showBridges("BR_t1_s1")
    print(f"Bridge was found: {found}")