from typing import List
from bson.objectid import ObjectId
from models.vpc_model import VPC, VPCStatus
from models.subnet_model import Subnet
from models.vm_model import VM, VMState
from models.interface_model import Interface
from models.tenant_model import Tenant
from constants.infra_constants import ROUTER_VM_VCPU, ROUTER_VM_MEM, ROUTER_VM_DISK_SIZE, HOST_NAT_NETWORK

import traceback

class VPCController:
    @staticmethod
    def add_subnet(db, vpc: VPC | str, subnet: Subnet | ObjectId |str ) -> bool:
        try:
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
            if not vpc:
                raise Exception("VPC not found")
            if isinstance(subnet, str):
                tmp = Subnet.find_by_name(db, subnet)
                if not tmp:
                    subnet = Subnet.find_by_id(db, ObjectId(subnet))
            elif isinstance(subnet, ObjectId):
                subnet = Subnet.find_by_id(db, subnet)
            if not subnet:
                raise Exception("Subnet not found")
            vpc.subnets.append(subnet.get_id())
            vpc.save(db)
            return True
        except:
            return False
    
    @staticmethod
    def remove_subnet(db, vpc: VPC | str, subnet: Subnet | ObjectId |str) -> bool:
        try:
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
            if not vpc:
                raise Exception("VPC not found")
            if isinstance(subnet, str):
                tmp = Subnet.find_by_name(db, subnet)
                if not tmp:
                    subnet = Subnet.find_by_id(db, ObjectId(subnet))
            elif isinstance(subnet, ObjectId):
                subnet = Subnet.find_by_id(db, subnet)
            if not subnet:
                raise Exception("Subnet not found")
            if subnet.get_id() in vpc.subnets:
                vpc.subnets.remove(subnet.get_id())
            vpc.save(db)
            return True
        except:
            return False
        
    @staticmethod
    def list_subnets(db, vpc: VPC | str) -> List[Subnet]:
        try:
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
            if not vpc:
                raise Exception("VPC not found")
            subnets = list(db.subnet.find({'_id': {'$in': vpc.subnets}}))
            return [Subnet.from_dict(i) for i in subnets]
        except:
            return False
        
    @staticmethod
    def create_subnet(db, tenant: Tenant | str, vpc: VPC | str, cidr: str, network_name: str, bridge_name: str) -> Subnet | None:
        try:
            if isinstance(tenant, str):
                tenant = Tenant.find_by_name(db, tenant)
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
            subnet = Subnet(cidr, network_name, bridge_name)
            subnet.save(db)
            vpc.subnets.append(subnet.get_id())
            vpc.save(db)
            if vpc.routerVM is None:
                VPCController.create_router(db, tenant, vpc)
                pass
            router_vm:VM = VM.find_by_id(db, vpc.routerVM)
            # TODO: WILL CHANGE
            print("router vm info", router_vm.name)
            router_vm.connect_to_network(db, subnet.get_id(), is_gateway=True, load_balancing_interface=False)
            return subnet
        except Exception as e :
            print('Exception occured', e)
            traceback.print_exc()
            return None
        
    @staticmethod
    def remove_subnet(db, vpc: VPC | str, cidr: str) -> bool:
        try:
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
            if not vpc:
                raise Exception("VPC not found")
            subnets: List[Subnet] = [Subnet.find_by_id(db, subnet_id) for subnet_id in vpc.subnets]
            subnet = None
            for i in subnets:
                if i.subnet == cidr:
                   subnet = i
            
            connected_interfaces = db.interface.find({'subnet_id': subnet})
            for_restart = []
            for interface in connected_interfaces:
                intf = Interface.from_dict(interface)
                vm = VM.find_by_id(db, intf.instance_id)
                if vm.state == VMState.RUNNING:
                    for_restart.append(vm.get_id())
                vm.undefine(db)
                vm.disconnect_from_network(db, subnet.get_id())
                
            for vm_id in for_restart:
                vm = VM.find_by_id(db, vm_id)
                vm.start(db)
            
            subnet.undefine(db)
            subnet.delete(db)
            
            vpc.subnets.remove(subnet.get_id())
            vpc.save(db)

            return True    
        except:
            return False
    
    @staticmethod        
    def create_router(db, tenant: Tenant | str, vpc: VPC | str):
        try:
            if isinstance(tenant, str):
                tenant = Tenant.find_by_name(db, tenant)
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
                if not vpc:
                    raise Exception("VPC not found")
            if vpc.routerVM is not None:
                return True
            name = f'RVM_{tenant.name.upper()}_{vpc.name.upper()}'
            router_vm = VM(name, ROUTER_VM_VCPU, ROUTER_VM_MEM, ROUTER_VM_DISK_SIZE)
            router_vm.save(db)
            sb = Subnet.find_by_name(db, HOST_NAT_NETWORK)
            router_vm.connect_to_network(db, sb.get_id(), default= True)
            vpc.routerVM = router_vm.get_id()
            vpc.save(db)
        except:
            return False
        
    @staticmethod
    def up(db, tenant: Tenant | str, vpc: VPC | str):
        try:
            if isinstance(tenant, str):
                tenant = Tenant.find_by_name(db, tenant)
            if isinstance(vpc, str):
                vpcs: List[VPC] = [VPC.find_by_id(i) for i in tenant.vpcs]
                for i in vpcs:
                    if i.name == vpc:
                        vpc = i
                        break
            if vpc.status == VPCStatus.RUNNING:
                return True
            elif vpc.status == VPCStatus.ERROR:
                VPCController.down(db, tenant, vpc)
            vpc.status = VPCStatus.CREATING
            vpc.save(db)
            try:
                sbs = [Subnet.find_by_id(db, i) for i in vpc.subnets]
                if vpc.routerVM is None:
                    VPCController.create_router(db, tenant, vpc)
                    for sb in sbs:
                        router_vm: VM = VM.find_by_id(db, vpc.routerVM)
                        router_vm.connect_to_network(db, sb.get_id(), is_gateway=True)
                for sb in sbs:
                    sb.define_net(db)
                router_vm: VM = VM.find_by_id(db, vpc.routerVM)
                router_vm.start(db)
            except:
                vpc.status = VPCStatus.ERROR
                vpc.save(db)
                return False
        except:
            return False
        return True
        
    @staticmethod
    def down(db, tenant: Tenant | str, vpc: VPC | str):
        try:
            if isinstance(tenant, str):
                tenant = Tenant.find_by_name(db, tenant)
            if isinstance(vpc, str):
                vpcs: List[VPC] = [VPC.find_by_id(i) for i in tenant.vpcs]
                for i in vpcs:
                    if i.name == vpc:
                        vpc = i
                        break
            if vpc.status == VPCStatus.UNDEFINED:
                return True
            try:
                router_vm: VM = VM.find_by_id(db, vpc.routerVM)
                router_vm.undefine(db)
                
                for sb_id in vpc.subnets:
                    sb: Subnet = Subnet.find_by_id(sb_id)
                    sb.undefine_net(db)
            except:
                vpc.status = VPCStatus.ERROR
                vpc.save(db)
        except:
            return False
        return True
    