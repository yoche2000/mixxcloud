# from models.vm_model import VM
# from models import  Tenant, VM
from controllers.vm_controller import VMController
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
    
    
    TENANT_NAME = 'Delta'
    tenant = Tenant.find_by_name(db, TENANT_NAME)
    if not tenant:
        tenant = Tenant(TENANT_NAME).save(db)
    
    VPC_NAME = 'vpc1'
    vpc = TenantController.get_vpc_by_tenant_vpc_name(db, tenant, VPC_NAME)
    if not vpc:
        vpc: VPC = TenantController.create_vpc(db, tenant, VPC_NAME, 'east')

    VPCController.down(db, tenant, vpc)
    
    


if __name__ == '__main__':
    if is_root():
        main()
        # console.main()
    else:
        print("Run the script as sudo")
        exit(1)