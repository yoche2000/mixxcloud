from ipaddress import IPv4Address, IPv4Network, ip_network
import random
from typing import List
from bson.objectid import ObjectId
from Container_automation.workflows import Container_CRUD_Workflows, Subnet_CRUD_Workflows
from controllers.container_controller import ContainerController
from models.container_model import Container, ContainerStatus
from controllers.subnet_controller import SubnetController
from controllers.vm_controller import VMController
from models.vpc_model import VPC, VPCStatus
from models.subnet_model import Subnet
from models.vm_model import VM, VMState
from models.interface_model import Interface
from models.tenant_model import Tenant
from constants.infra_constants import HOST_PUBLIC_NETWORK, REGION_MAPPING, ROUTER_VM_VCPU, ROUTER_VM_MEM, ROUTER_VM_DISK_SIZE, HOST_NAT_NETWORK
from utils.ip_utils import IPUtils

import traceback

class VPCController:        
    @staticmethod
    def list_subnets(db, vpc: VPC | str) -> List[Subnet]:
        try:
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
            if not vpc:
                raise Exception("VPC not found")
            subnets = list(db.subnet.find({'_id': {'$in': vpc.subnets}}))
            #print("Subnets from List_Subnets:", subnets)
            return [Subnet.from_dict(i) for i in subnets]
        except Exception as error:
            print("Error from List_SubNets:", error)
            return False
        
    # use
    @staticmethod
    def create_subnet(db, tenant: Tenant | str, vpc: VPC | str, cidr: str, network_name: str) -> Subnet | None:
        try:
            if isinstance(tenant, str):
                tenant = Tenant.find_by_name(db, tenant)
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
            subnets: List[Subnet] = VPCController.list_subnets(db, vpc)
            print("Returned Subnets for the VPC:",subnets)
            conflict = False
            sb_nw = Subnet(cidr, network_name, network_name)
            cidr: IPv4Network = sb_nw.get_ipobj()
            if db.subnet.find_one({"network_name":network_name}):
                print(f"Cannot create network with libvirt {network_name} - Conflict exists")
                return None
            for subnet in subnets:
                if cidr.overlaps(subnet.get_ipobj()) or subnet.network_name == network_name:
                    conflict = True
                    break
            if conflict:
                print(f"Cannot create subnet with {cidr} - Conflict exists")
                return None
            sb_nw.save(db)
            vpc.subnets.append(sb_nw.get_id())
            vpc.save(db)

            # VMController.undefine(db, vpc.routerVM)
            ContainerController.connect_to_network(db, vpc.get_id(), sb_nw.get_id(), None, False)

            return sb_nw
        except Exception as e :
            print('Exception occured', e)
            traceback.print_exc()
            return None
        
    # use
    @staticmethod
    def remove_subnet(db, vpc: VPC | str, network_name: str) -> bool:
        try:
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
            if not vpc:
                raise Exception("VPC not found")
            subnets: List[Subnet] = []
            for subnet_id in vpc.subnets:
                subnetID = Subnet.find_by_id(db, subnet_id) 
                if subnetID is not None:
                    subnets.append(subnetID)
            print(f"Subnets attached to the VPC: {subnets}")
            subnet = None
            for i in subnets:
                if i.network_name == network_name:
                   subnet = i
            SubnetController.undefine(db, subnet)
            connected_interfaces = db.interface.find({'subnet_id': subnet.get_id()})
            print(f"All the attached interfaces to the subnet for the Subnet - {subnet.network_name} are: {connected_interfaces}.")
            for_restart = []
            for interface in connected_interfaces:
                print("Entered the loop..")
                intf = Interface.from_dict(interface)
                vm = VM.find_by_id(db, intf.instance_id)
                if vm.state == VMState.RUNNING:
                    for_restart.append(vm.get_id())
                print("VM ID Before Shutdown:", vm.get_id())
                VMController.undefine(db, vm.get_id())
                VMController.disconnect_from_network(db, vm.get_id(), subnet.get_id())
                
            for vm_id in for_restart:
                print("Restarting the VM:", vm_id)
                vm = VM.find_by_id(db, vm_id)
                VMController.define(db,vm.get_id())
                VMController.start(db,vm.get_id())
                # vm.start(db)
            
            
            subnet_ = subnet.get_id()
            subnet.delete(db)
            print(f"Subnet which is being removed is: {subnet.get_id()}")
            vpc.subnets.remove(subnet_)
            vpc.save(db)

            return True    
        except Exception as error:
            print(f"Issue in deleting the Subnet. Error details: {error}")
            return False
    
    @staticmethod        
    def create_router(db, tenant: Tenant | str, vpc: VPC | str):
        print('Create router called')
        try:
            if isinstance(tenant, str):
                tenant = Tenant.find_by_name(db, tenant)
            if isinstance(vpc, str):
                vpc = VPC.find_by_name(db, vpc)
                if not vpc:
                    raise Exception("VPC not found")
            if vpc.container_east is not None:
                return True
            
            name = f'{tenant.name.upper()}{vpc.name.upper()}'
            # router_vm = VM(name, ROUTER_VM_VCPU, ROUTER_VM_MEM, ROUTER_VM_DISK_SIZE, vpc.get_id(), isRouterVM = True)
            # router_vm.save(db)
            
            sb = Subnet.find_by_name(db, HOST_NAT_NETWORK)
            
            container_east = Container(name, 'vpcrouter', 'east', None, None).save(db)
            container_west = Container(name, 'vpcrouter', 'west', None, None).save(db)
            
            ContainerController.create(db, container_east.get_id())
            ContainerController.create(db, container_west.get_id())
            
            ContainerController.connect_to_network(db, container_east.get_id(), sb.get_id(), is_nat=True, default_route=IPUtils.get_default_subnet_gateway(db, sb.get_id(), container_east.region))
            ContainerController.connect_to_network(db, container_west.get_id(), sb.get_id(), is_nat=True, default_route=IPUtils.get_default_subnet_gateway(db, sb.get_id(), container_west.region))
            
            vpc.container_east = container_east.get_id()
            vpc.container_west = container_west.get_id()
            vpc.save(db)
            
            return True
        except:
            traceback.print_exc()
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
                        VMController.connect_to_network(db, vpc.get_id(), sb, vpc.routerVM, is_gateway=True)
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
    
    @staticmethod
    def unique_public_ip(db):
        public_net = Subnet.find_by_name(db, HOST_PUBLIC_NETWORK)
        subnet_nw = public_net.get_ipobj()
        sb_nw = subnet_nw.hosts()

        used_ips: set[IPv4Address] = {IPv4Address(item['ip_address']) for item in db.interface.find({"subnet_id": public_net.get_id()})}
        used_ips.add(subnet_nw[1])
        i = 2
        while True:
            ip_address = next(sb_nw, i)
            if ip_address not in used_ips:
                break
            else:
                i = random.randrange(10)
        ip_address = str(ip_address)
        return ip_address
    
    @staticmethod
    def create_subnet_in_container(db, vpc_id: ObjectId, subnet_name: str, cidr: str, ):
        try:
            vpc = VPC.find_by_id(db, vpc_id)
            cont_even = Container.find_by_id(db, vpc.container_west)
            cont_odd = Container.find_by_id(db, vpc.container_east)
            
            _inf_even = Interface.find_by_id(db, cont_even.interfaces[0])
            _inf_odd = Interface.find_by_id(db, cont_odd.interfaces[0])
            
            if cont_even.status == ContainerStatus.ERROR or cont_even.status == ContainerStatus.UPDATING:
                    return True
            if cont_odd.status == ContainerStatus.ERROR or cont_odd.status == ContainerStatus.UPDATING:
                    return True
            
            cont_even.status = ContainerStatus.UPDATING
            cont_odd.status = ContainerStatus.UPDATING
            cont_even.save(db)
            cont_odd.save(db)
            
            container_name = cont_even.name
            
            nw_obj = ip_network(cidr)
            
            pipeline = [
                {"$group": {"_id": None, "maxValue": {"$max": "$vni_id"} }}
            ]
            sb_max_vni = list(db['subnet'].aggregate(pipeline))[0]['maxValue']
            if sb_max_vni < 10:
                sb_max_vni = 9
                
            vni_id = sb_max_vni + 1
            print(cont_even.name+subnet_name)
            sb = Subnet(cidr, cont_even.name+subnet_name, cont_even.name+subnet_name, vni_id, vpc_id).save(db)
            vpc.subnets.append(sb.get_id())
            vpc.save(db)
            
            Container_CRUD_Workflows.run_ansible_playbook_for_container_subnet_creation(
                container_name,
                subnet_name,
                cidr,
                f"{str(nw_obj[2])}/{cidr.split('/')[1]}",
                vni_id,
                _inf_even.ip_address,
                _inf_odd.ip_address,
                region = REGION_MAPPING[cont_even.region],
                )
            Container_CRUD_Workflows.run_ansible_playbook_for_container_subnet_creation(
                container_name,
                subnet_name,
                cidr,
                f"{str(nw_obj[1])}/{cidr.split('/')[1]}",
                vni_id,
                _inf_odd.ip_address,
                _inf_even.ip_address,
                region = REGION_MAPPING[cont_odd.region]
                )
            cont_even.status = ContainerStatus.RUNNING
            cont_odd.status = ContainerStatus.RUNNING
            cont_even.save(db)
            cont_odd.save(db)
            return sb
        except:
            traceback.print_exc()
            cont_even.status = ContainerStatus.ERROR
            cont_odd.status = ContainerStatus.ERROR
            cont_even.save(db)
            cont_odd.save(db)
            return None
    
    @staticmethod
    def delete_subnet_in_container(db, vpc_id: ObjectId, subnet_name: str ):
        try:
            vpc = VPC.find_by_id(db, vpc_id)
            container_name = Container.find_by_id(db, vpc.container_east).name
            subnet = Subnet.find_by_name(db, container_name+subnet_name)
            vni_id = subnet.vni_id
            
            Subnet_CRUD_Workflows.run_ansible_playbook_for_subnet_deletion(container_name, subnet_name, vni_id)
            vpc.subnets.remove(subnet.get_id())
            subnet.delete(db)
            vpc.status = VPCStatus.RUNNING
            vpc.save(db)
        except:
            vpc.status = VPCStatus.ERROR
            vpc.save(db)
            return False
    