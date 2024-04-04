# from models.vm_model import VM
# from models import  Tenant, VM
from controllers.vm_controller import VMController
from models.db_model import DB
from models.vm_model import VM, VMState
from models.tenant_model import Tenant
from models.interface_model import Interface
from models.subnet_model import Subnet, SubnetStatus, SubnetType
from models.vpc_model import VPC
from models.lb_model import LBType
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
    
    # if infra_sb.status != SubnetStatus.RUNNING and infra_sb.status != SubnetStatus.ERROR:
    #     print(f"Defining {HOST_NAT_NETWORK}")
    #     # infra_sb.define_net(db)
    #     SubnetController.define(db, None, None, infra_sb)

    public_sb =  Subnet.find_by_name(db, HOST_PUBLIC_NETWORK)
    if not public_sb:
        print(f"Creating {HOST_PUBLIC_NETWORK}")
        public_sb = Subnet(HOST_PUBLIC_SUBNET, HOST_PUBLIC_NETWORK, HOST_PUBLIC_BR_NAME).save(db)
    

    # if public_sb.status != SubnetStatus.RUNNING and public_sb.status != SubnetStatus.ERROR:
    #     print(f"Defining {HOST_PUBLIC_NETWORK}")
    #     # public_sb.define_net(db)
    #     SubnetController.define(db, None, None, public_sb)


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
    
    """
    TENANT_NAME = 'A'
    tenant = Tenant.find_by_name(db, TENANT_NAME)
    if not tenant:
        tenant = Tenant(TENANT_NAME).save(db)
    
    TENANT_NAME = 'B'
    tenant = Tenant.find_by_name(db, TENANT_NAME)
    if not tenant:
        tenant = Tenant(TENANT_NAME).save(db)
    """
    """
    VPC_NAME = 'VPC7'
    vpc = TenantController.get_vpc_by_tenant_vpc_name(db, tenant, VPC_NAME)
    if not vpc:
        vpc: VPC = TenantController.create_vpc(db, tenant, VPC_NAME, 'east')
    """
    # vpc.
    # VPCController.down(db, tenant, vpc)
    """
    VPCController.up(db, tenant, vpc)
    
    customer_sb = Subnet.find_by_id(db, vpc.subnets[0])
    vm = VM.find_by_id(db, vpc.routerVM)
    vm.state = VMState.UNDEFINED
    vm.save(db)
    """
    # vm = VM.find_by_id(db, vpc.routerVM)
    # vm.state = VMState.ERROR
    # vm.save(db)

    # VPCController.up(db, tenant, vpc)


    # VPCController.down(db, tenant, vpc)
        
    # customer_subnet = Subnet('10.11.10.0/24', 'CS_NW_1', 'CS_BR_2').save(db)
    # SubnetController.define(db, tenant, vpc, customer_subnet)

    # VPCController.create_subnet(db, tenant, vpc, '10.15.15.0/24', 'CS_NW_3', 'CS_BR_3')    
    # VPCController.create_subnet(db, tenant, vpc, '10.15.15.0/24', 'CS_NW_3', 'CS_BR_3')
    
    # vm1 = VM('test_vm', 1, 1, '10G').save(db)

    
    
    # VPCController.up(db, tenant, vpc)
# 
    
    # VMController.connect_to_network(db, customer_subnet.get_id(), vm1.get_id(), default=True)
    
    # VPCController.up(db, tenant, vpc)
    # VMController.define(db, vm1.get_id())
    
    # customer_subnet = Subnet('10.11.10.0/24', 'CS_NW_1', 'CS_NW_2')
    
    
    # VMController.connect_to_network(db, customer_subnet.get_id(), vm1.get_id(), default=True)
    
    # VPCController.up(db, tenant, vpc)
    
    
    # vm1 = VM.find_by_name(db, 'Cst_VM1').save(db)
    # vm2 = VM.find_by_name(db, 'Cst_VM2').save(db)
    # vm3 = VM.find_by_name(db, 'Cst_VM3').save(db)
    # vm1 = VM('Cst_VM1', 1, 1024, '10G', vpc.get_id()).save(db)
    # vm2 = VM('Cst_VM2', 1, 1024, '10G', vpc.get_id()).save(db)
    # vm3 = VM('Cst_VM3', 1, 1024, '10G', vpc.get_id()).save(db)
    
    # VMController.connect_to_network(db, vpc.get_id(), customer_sb.get_id(), vm1.get_id(), default=True)
    # VMController.connect_to_network(db, vpc.get_id(), customer_sb.get_id(), vm2.get_id(), default=True)
    # VMController.connect_to_network(db, vpc.get_id(), customer_sb.get_id(), vm3.get_id(), default=True)
    
    # VMController.start(db, vm1.get_id())
    # VMController.start(db, vm2.get_id())
    # VMController.start(db, vm3.get_id())
    
    # VMController.create_load_balancer(db, vpc,  vpc.routerVM, 'app1', '10.10.10.3', LBType.IAAS)
    # VMController.rm_load_balancer(db, vpc,  vpc.routerVM, 'app1')
    
    # VMController.add_lb_ip_target(db, vpc.routerVM, 'app1', '10.15.15.2')
    # VMController.add_lb_ip_target(db, vpc.routerVM, 'app1', '10.15.15.3')
    # VMController.add_lb_ip_target(db, vpc.routerVM, 'app1', '10.15.15.4')
    
    
    
    
    
    
    


if __name__ == '__main__':
    if is_root():
        main()
    else:
        print("Run the script as sudo")
        exit(1)