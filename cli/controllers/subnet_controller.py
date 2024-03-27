import os
import subprocess
import traceback

class SubnetController:
    @staticmethod
    def define(network_name: str,bridge_name: str, success, failure):
        try:
            br = SubnetController.create_bridge(bridge_name)
            nw = SubnetController.create_network(network_name)
            if br and nw:
                success()
            else:
                failure()
        except Exception as e:
            traceback.print_exc()
            failure()
    
    @staticmethod
    def create_bridge(bridgename: str):
        SubnetController.check_is_not_empty(bridgename)
        os.system("brctl addbr "+bridgename)
        os.system("sudo ip link set up "+bridgename)
        t = subprocess.check_output("ip link show "+bridgename, shell=True)
        if not "UP" in str(t):
            raise Exception("Error creating bridge")
        return True

    @staticmethod            
    def create_network(network_name: str):
        return True
    
    @staticmethod
    def undefine(network_name: str, bridge_name: str, success, failure):
        print(f"Undefine {network_name}")
        try:
            br = SubnetController.destroy_bridge(bridge_name)
            nw = SubnetController.destory_network(network_name)
            if br and nw:
                success()
            else:
                failure()
        except Exception as e:
            traceback.print_exc()
            failure()
    
    @staticmethod
    def destroy_bridge(bridge_name: str):
        SubnetController.check_is_not_empty(bridge_name)
        os.system("sudo ip link set down "+bridge_name)
        os.system("brctl delbr "+bridge_name)
        try:
            subprocess.check_output(f"brctl show | grep {bridge_name}")
            raise Exception("Bridge exists after deletion")
        except:
            return True
    @staticmethod
    def destory_network(bridge_name: str):
        return True
    
    @staticmethod
    def check_resource_status():
        pass
    
    @staticmethod
    def showBridges(bridgename: str):
        SubnetController.check_is_not_empty(bridgename)
        if not bridgename:
            raise Exception("bridgename is required")
        os.system("sudo brctl show | grep "+bridgename)

    @staticmethod
    def rmBridge(bridgename: str, success, failure):
        SubnetController.check_is_not_empty(bridgename)
        os.system("sudo ip link set down "+bridgename)
        os.system("brctl delbr "+bridgename)
        try:
            t = subprocess.check_output(f"brctl show | grep {bridgename}")
            failure()
        except:
            success()

    @staticmethod
    def isRunning(bridgename: str):
        SubnetController.check_is_not_empty(bridgename)
        t = subprocess.check_output("sudo brctl show", shell=True)
        return bridgename in str(t)
        
    @staticmethod
    def check_is_not_empty(txt):
        if not txt:
            raise Exception("bridgename is required")

if __name__ == '__main__':
    found = SubnetController.showBridges("BR_t1_s1")
    print(f"Bridge was found: {found}")