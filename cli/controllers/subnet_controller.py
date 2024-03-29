import os
import subprocess
import traceback
from ipaddress import ip_network
from models.subnet_model import SubnetStatus, Subnet, SubnetType
from models.tenant_model import Tenant
from models.vpc_model import VPC

class SubnetController:
    @staticmethod
    def define(db, tenant: Tenant | str | None , vpc: VPC | str | None, subnet: Subnet):
        if not isinstance(subnet, Subnet):
            raise Exception("expect subnet of type Subnet")
        try:
            if tenant is None:
                pass
            elif isinstance(tenant, str):
                tenant = Tenant.find_by_name(db, tenant)
            if vpc is None:
                pass
            elif isinstance(vpc, str):
                for i in tenant.vpcs:
                    tmp = VPC.find_by_id(db, i)
                    if tmp.name == vpc:
                        vpc = tmp
                        break
            if subnet.status == SubnetStatus.RUNNING:
                print("Subnet is already running")
                return True
            if subnet.status == SubnetStatus.STARTING or subnet.status == SubnetStatus.UPDATING:
                # don't update status since someother action is being performed on this object
                print("Cannot update at his time")
                return
            if subnet.status == SubnetStatus.ERROR:
                SubnetController.undefine(db, subnet)
            subnet.status = SubnetStatus.STARTING
                    
            network_name = subnet.network_name
            bridge_name = subnet.bridge_name
            cidr = subnet.subnet
            nat_enabled = SubnetType.NAT == subnet.subnet_type
            print(f"Define {network_name}")
            br = nat_enabled or SubnetController.create_bridge(bridge_name)
            nw = SubnetController.create_network(network_name, bridge_name, cidr, nat_enabled)
            if br and nw:
                subnet.status = SubnetStatus.RUNNING
                subnet.save(db)
            else:
                subnet.status = SubnetStatus.ERROR
                subnet.save(db)
        except Exception as e:
            traceback.print_exc()
            subnet.status = SubnetStatus.ERROR
            subnet.save(db)
    
    
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
    def create_network(network_name: str, bridge_name: str, cidr: str, nat_enabled: bool):
        try:
            if nat_enabled:
                template_path = './templates/libvirt_network_route.xml'
            else:
                template_path = './templates/libvirt_network_bridge.xml'
            newpath = '/etc/libvirt/qemu/networks/subnets/' + network_name + '.xml'
            
            cidr = ip_network(cidr)
            
            options = {'NETWORKNAME': network_name,
                    'BRIDGENAME': bridge_name,
                    'ROUTERIP': cidr[1],
                    'NETMASK': cidr.netmask,
                    'HOSTIPSTART': cidr[2],
                    'HOSTIPEND': cidr[-1]
                    }
            
            with open(template_path, 'r') as file:
                data = file.read()
                for key in options.keys():
                    data = data.replace(key, str(options[key]))
            
            with open(newpath, 'w') as out_file:
                out_file.write(data)

            os.system("sudo virsh net-define "+newpath)
            os.system("sudo virsh net-start "+network_name)
            return True
        except:
            traceback.print_exc()
            return False
    
    @staticmethod
    def undefine(db, subnet: Subnet):
        print(subnet.json())
        if not isinstance(subnet, Subnet):
            raise Exception("expect subnet of type Subnet")
        try:
            if subnet.status == SubnetStatus.UNDEFINED:
                return True
            if subnet.status == SubnetStatus.STARTING or subnet.status == SubnetStatus.UPDATING:
                # don't update status since someother action is being performed on this object
                print("Cannot update at his time")
                return 
            subnet.status = SubnetStatus.DELETING
            subnet.save(db)
            network_name = subnet.network_name
            bridge_name = subnet.bridge_name
            nat_enabled = SubnetType.NAT == subnet.subnet_type
            print(f"Undefine {network_name}")
            br = nat_enabled or SubnetController.destroy_bridge(bridge_name)
            nw = SubnetController.destory_network(network_name)
            if br and nw:
                subnet.status = SubnetStatus.UNDEFINED
                subnet.save(db)
            else:
                subnet.status = SubnetStatus.ERROR
                subnet.save(db)
        except Exception:
            traceback.print_exc()
            subnet.status = SubnetStatus.ERROR
            subnet.save(db)
    
    @staticmethod
    def destroy_bridge(bridge_name: str):
        SubnetController.check_is_not_empty(bridge_name)
        print("destroy bridge", bridge_name)
        os.system("sudo ip link set down "+bridge_name)
        os.system("brctl delbr "+bridge_name)
        try:
            subprocess.check_output(f"brctl show | grep {bridge_name}")
            raise Exception("Bridge exists after deletion")
        except:
            return True
    @staticmethod
    def destory_network(network_name: str):
        print("destroy network", network_name)
        try:
            path = '/etc/libvirt/qemu/networks/subnets/' + network_name + '.xml'
            os.system("sudo rm " + path)
            os.system("sudo virsh net-undefine " + network_name)
            os.system("sudo virsh net-destroy " + network_name)
            return True
        except:
            traceback.print_exc()
            return False
    
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