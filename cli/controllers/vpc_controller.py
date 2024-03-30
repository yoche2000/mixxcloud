from ipaddress import IPv4Network
from typing import List
from bson.objectid import ObjectId
from controllers.subnet_controller import SubnetController
from controllers.vm_controller import VMController
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
        
    # use
    @staticmethod
    def create_subnet(db, tenant: Tenant | str, vpc: VPC | str, cidr: str, network_name: str, bridge_name: str) -> Subnet | None:
        try:
            if isinstance(tenant, str):
                tenant = Tenant.find_by_name(db, tenant)
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
            subnets: List[Subnet] = VPCController.list_subnets(db, vpc)
            conflict = False
            tmp = Subnet(cidr, network_name, bridge_name)
            cidr: IPv4Network = tmp.get_ipobj()
            for subnet in subnets:
                if cidr.overlaps(subnet.get_ipobj()):
                    conflict = True
                    break
            if conflict:
                print(f"Cannot create subnet with {cidr} - Conflict exists")
                return None
            tmp.save(db)
            vpc.subnets.append(tmp.get_id())
            vpc.save(db)
            if vpc.routerVM is None:
                VPCController.create_router(db, tenant, vpc)
            # router_vm:VM = VM.find_by_id(db, vpc.routerVM)
            VMController.undefine(db, vpc.routerVM)
            VMController.connect_to_network(db, tmp.get_id(), vpc.routerVM, is_gateway=True)
            
            # TODO: Modify states for when VPC is running
            if vpc.status == VPCStatus.RUNNING:
                SubnetController.define(db, tenant, vpc, tmp)
                VMController.start(db, vpc.routerVM)

            return tmp
        except Exception as e :
            print('Exception occured', e)
            traceback.print_exc()
            return None
        
    # use
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
                VMController.undefine(db, vm.get_id())
                VMController.disconnect_from_network(db, vm.get_id(), subnet.get_id())
                
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
            router_vm = VM(name, ROUTER_VM_VCPU, ROUTER_VM_MEM, ROUTER_VM_DISK_SIZE, isRouterVM = True)
            router_vm.save(db)
            vpc.routerVM = router_vm.get_id()
            vpc.save(db)
            
            sb = Subnet.find_by_name(db, HOST_NAT_NETWORK)
            VMController.connect_to_network(db, sb.get_id(), router_vm.get_id(), default=True)
            return True
        except:
            return False
    
    # use
    @staticmethod
    def up(db, tenant: Tenant | str, vpc: VPC | str):
        try:
            if isinstance(tenant, str):
                tenant = Tenant.find_by_name(db, tenant)
            if isinstance(vpc, str):
                vpcs: List[VPC] = [VPC.find_by_id(db, i) for i in tenant.vpcs]
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
                sbs = vpc.subnets
                if vpc.routerVM is None:
                    VPCController.create_router(db, tenant, vpc)
                    for sb in sbs:
                        VMController.connect_to_network(db, sb, vpc.routerVM, is_gateway=True)
                for sb in sbs:
                    SubnetController.define(db, tenant, vpc, Subnet.find_by_id(db, sb))
                VMController.start(db, vpc.routerVM)
                vpc.status = VPCStatus.RUNNING
                vpc.save(db)
            except:
                traceback.print_exc()
                vpc.status = VPCStatus.ERROR
                vpc.save(db)
                return False
        except:
            traceback.print_exc()
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
                VMController.undefine(db, vpc.routerVM)
                for sb_id in vpc.subnets:
                    SubnetController.undefine(db, Subnet.find_by_id(db, sb_id))
                vpc.status = VPCStatus.UNDEFINED
                vpc.save(db)
            except:
                traceback.print_exc()
                vpc.status = VPCStatus.ERROR
                vpc.save(db)
        except:
            traceback.print_exc()
            return False
        return True
    