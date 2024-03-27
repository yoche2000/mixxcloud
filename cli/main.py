# from models.vm_model import VM
# from models import  Tenant, VM
from models.db_model import DB
from models.vm_model import VM
from models.tenant_model import Tenant
from models.interface_model import Interface
from models.subnet_model import Subnet
from models.vpc_model import VPC
# from models.vpc_model import VPC
import traceback
from utils.utils import Utils
from constants.infra_constants import *

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
    
    if not Subnet.find_by_name(db, 'infra'):
        print("Creating infra subnet")
        infra_sb = Subnet(HOST_NAT_SUBNET, HOST_NAT_NETWORK, HOST_NAT_BR_NAME).save(db)

    if not Subnet.find_by_name(db, 'public'):
        print("Creating public subnet")
        public_sb = Subnet(HOST_PUBLIC_SUBNET, HOST_PUBLIC_NETWORK, HOST_PUBLIC_BR_NAME).save(db)
    
    # infra_sb.define_net(db)
    infra_sb.undefine_net(db)
    
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
    main()