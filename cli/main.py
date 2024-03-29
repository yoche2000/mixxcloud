# from models.vm_model import VM
# from models import  Tenant, VM
from models.db_model import DB
from models.vm_model import VM, VMState
from models.tenant_model import Tenant
from models.interface_model import Interface
from models.subnet_model import Subnet, SubnetStatus, SubnetType
from models.vpc_model import VPC
# from models.vpc_model import VPC
import traceback
from utils.utils import Utils
from constants.infra_constants import *
import os
import console
from controllers.tenant_controller import TenantController
from controllers.vpc_controller import VPCController
from controllers.subnet_controller import SubnetController

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
        # infra_sb.define_net(db)
        SubnetController.define(db, None, None, infra_sb)

    public_sb =  Subnet.find_by_name(db, HOST_PUBLIC_NETWORK)
    if not public_sb:
        print(f"Creating {HOST_PUBLIC_NETWORK}")
        public_sb = Subnet(HOST_PUBLIC_SUBNET, HOST_PUBLIC_NETWORK, HOST_PUBLIC_BR_NAME).save(db)
    
    if public_sb.status != SubnetStatus.RUNNING and public_sb.status != SubnetStatus.ERROR:
        print(f"Defining {HOST_PUBLIC_NETWORK}")
        # public_sb.define_net(db)
        SubnetController.define(db, None, None, public_sb)

    """
    # sb = Subnet('192.168.10.0/24', 'L2', 'brl2').save(db)
    # sb.define_net(db)
    
    # sb.undefine_net(db)
    # sb.delete(db)
    """
    
    
    # USE THIS COMMAND TO UNDEFINE
    # SubnetController.undefine(db, public_sb)
    # public_sb.delete(db)
    # SubnetController.undefine(db, infra_sb)
    # infra_sb.delete(db)
    
    
    TENANT_NAME = 'Alfred'
    tenant = Tenant.find_by_name(db, TENANT_NAME)
    if not tenant:
        tenant = Tenant(TENANT_NAME).save(db)
    
    print("----------------")
    VPC_NAME = 'test_vpc'
    vpc = TenantController.get_vpc_by_tenant_vpc_name(db, tenant, VPC_NAME)
    if not vpc:
        vpc: VPC = TenantController.create_vpc(db, tenant, VPC_NAME, 'east')
    # vpc.up(db)
    
    # print(vpc.name)
    max_length_of_name = 15
    SUBNET_NAME_1 = f"NW_{TENANT_NAME[:2].upper()}_{VPC_NAME[:2].upper()}_1"
    SUBNET_NAME_BR_1 = f"BR_{TENANT_NAME[:2].upper()}_{VPC_NAME[:2].upper()}_1"
    subnet1 = Subnet.find_by_name(db, SUBNET_NAME_1)
    if not subnet1:
        subnet1 = VPCController.create_subnet(db, tenant, vpc, '192.168.50.0/24', SUBNET_NAME_1, SUBNET_NAME_BR_1)
    # SubnetController.define(db, tenant, vpc, subnet1)
    SubnetController.undefine(db, subnet1)
    
    SUBNET_NAME_2 = f"NW_{TENANT_NAME[:2].upper()}_{VPC_NAME[:2].upper()}_2"
    SUBNET_NAMEB_BR_2 = f"BR_{TENANT_NAME[:2].upper()}_{VPC_NAME[:2].upper()}_2"
    subnet2 = Subnet.find_by_name(db, SUBNET_NAME_2)
    if not subnet2:
        subnet2 = VPCController.create_subnet(db, tenant, vpc, '192.168.51.0/24', SUBNET_NAME_2, SUBNET_NAMEB_BR_2)
    # SubnetController.define(db, tenant, vpc, subnet2)
    SubnetController.undefine(db, subnet2)

    vm:VM = VM.find_by_name(db, 'test_vm')
    if vm:
        vm.undefine(db)
        vm.delete(db)
    # vm = VM('test_vm', 1, 1, 10).save(db)
    # vm.connect_to_network(db, subnet1.get_id(), default=True)
    # vm.connect_to_network(db, subnet2.get_id())
    # vm.start(db)
    
    # # vm.state = VMState.ERROR
    # # print(vm.name)
    # vm.undefine(db)
    # # vm.connect_to_network(db, subnet1.get_id(), default=True)
    # # vm.connect_to_network(db, subnet2.get_id())
    # # vm.save(db)
    # # vm.start(db)
    # vm.undefine(db)
    # vm.delete(db)
    
    # subs = vpc.list_subnets()
    # sb1 = vpc.create_subnet(db, '192.168.10.0/30', 'ALFRED_VPC1_SB1', 'ALFRED_VPC1_BR1')
    # sb2 = vpc.create_subnet(db, '192.30.20.0/30', 'ALFRED_VPC1_SB2', 'ALFRED_VPC1_BR1')
    # sb1.define_net(db)
    
    # vm2 = VM('TENANT_VM1', 1, 1, '10G').save(db)
    # vm2.connect_to_network

    # vm2.connect_to_network(db, sb1.get_id(), default=True)
    # # vm2.connect_to_network(db, sb2.get_id())
    
    # vm2.start(db)
    # # sb3 = vpc.create_subnet(db, '192.30.21.0/30', 'vm_net_3', 'br_net_3')
    # # sb4 = vpc.create_subnet(db, '192.30.22.0/30', 'vm_net_4', 'br_net_4')
    
    # vm = VM('VM1', 1, 1, 10).save(db)
    
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
        # console.main()
    else:
        print("Run the script as sudo")
        exit(1)