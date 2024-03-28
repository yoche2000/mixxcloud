# from models.vm_model import VM
# from models import  Tenant, VM
from models.db_model import DB
from models.vm_model import VM
from models.tenant_model import Tenant
from models.interface_model import Interface
from models.subnet_model import Subnet, SubnetStatus, SubnetType
from models.vpc_model import VPC
# from models.vpc_model import VPC
import traceback
from utils.utils import Utils
from constants.infra_constants import *
import os

def is_root():
    return os.geteuid() == 0

def print_resources(db):
    print("Tenant ===========")
    tenants = db.tenant.find({})
    for tenant in tenants:
        Tenant.from_dict(tenant).json()
        print('--------------')
        

    print("VPC ===========")
    vpcs = db.vpc.find({})
    for vpc in vpcs:
        VPC.from_dict(vpc).json()
        print('--------------')
    
    print("Subnet ===========")
    subnets = db.subnet.find({})
    for subnet in subnets:
        Subnet.from_dict(subnet).json()
        print('--------------')
        

    print("VMS ===========")
    vms = db.vm.find({})
    for vm in vms:
        VM.from_dict(vm).json()
        print('--------------')
        

    print("Interfaces ===========")
    interfaces = db.interface.find({})
    for interface in interfaces:
        Interface.from_dict(interface).json()
        print('--------------')
        

def main():
    db1 = DB()
    try:
        client = db1.get_client()
    except Exception:
        traceback.print_exc()
        exit(1)
    db = client['ln']
    
    infra_sb = Subnet.find_by_name(db, HOST_NAT_NETWORK)
    if not infra_sb:
        print(f"Creating {HOST_NAT_NETWORK}")
        infra_sb = Subnet(HOST_NAT_SUBNET, HOST_NAT_NETWORK, HOST_NAT_BR_NAME, subnet_type = SubnetType.NAT.name).save(db)
    
    if infra_sb.status != SubnetStatus.RUNNING and infra_sb.status != SubnetStatus.ERROR:
        print(f"Defining {HOST_NAT_NETWORK}")
        infra_sb.define_net(db)

    public_sb =  Subnet.find_by_name(db, HOST_PUBLIC_NETWORK)
    if not public_sb:
        print(f"Creating {HOST_PUBLIC_NETWORK}")
        public_sb = Subnet(HOST_PUBLIC_SUBNET, HOST_PUBLIC_NETWORK, HOST_PUBLIC_BR_NAME).save(db)
    
    if public_sb.status != SubnetStatus.RUNNING and public_sb.status != SubnetStatus.ERROR:
        print(f"Defining {HOST_PUBLIC_NETWORK}")
        public_sb.define_net(db)

            
    # sb = Subnet('192.168.10.0/24', 'L2', 'brl2').save(db)
    # sb.define_net(db)
    
    # sb.undefine_net(db)
    # sb.delete(db)
    
    # USE THIS COMMAND TO UNDEFINE
    # public_sb.undefine_net(db)
    # public_sb.delete(db)
    # infra_sb.undefine_net(db)
    # infra_sb.delete(db)
    
    
    
    # tenant = Tenant.find_by_name(db, 'Alfred')
    # if not Tenant.find_by_name(db, 'Alfred'):
    #     tenant = Tenant('Alfred').save(db)
    
    # vpc = tenant.get_vpc_by_name(db, 'vpc1')
    # if not vpc:
    #     vpc: VPC = tenant.create_vpc(db, 'vpc1', 'east')

    # sb1 = vpc.create_subnet(db, '192.168.10.0/30', 'vm_net_1', 'br_net_1')
    # sb2 = vpc.create_subnet(db, '192.30.20.0/30', 'vm_net_2', 'br_net_2')
    # sb3 = vpc.create_subnet(db, '192.30.21.0/30', 'vm_net_3', 'br_net_3')
    # sb4 = vpc.create_subnet(db, '192.30.22.0/30', 'vm_net_4', 'br_net_4')
    
    # vm = VM('VM1', 1, 1, 10).save(db)
    
    # vm.connect_to_network(db, sb1.get_id(), default=True)
    # vm.connect_to_network(db, sb2.get_id(), load_balancing_interface = True)
    # vm.connect_to_network(db, sb3.get_id(), load_balancing_interface = True)
    # vm.connect_to_network(db, sb4.get_id(), load_balancing_interface = False)
    # # vm.connect_to_network(db, sb2.get_id(), load_balancing_interface =True)
    # vm.connect_to_network(db, public_sb.get_id(), load_balancing_interface = True)
    
    # for interface in vm.list_interfaces(db):
    #     print(vm.name, interface.interface_name, Subnet.find_by_id(db, interface.subnet_id).network_name )
    # # print_resources(db)


if __name__ == '__main__':
    if is_root():
        main()
    else:
        print("Run the script as sudo")
        exit(1)