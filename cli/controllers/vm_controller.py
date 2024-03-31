from ipaddress import IPv4Address
import random
import traceback
from bson.objectid import ObjectId
from models.vpc_model import VPC
from models.lb_model import LoadBalancer, LBType
from models.interface_model import Interface
from models.vm_model import VM, VMState
from models.subnet_model import Subnet
from commands import VM_CRUD_Workflows, ROUTER_CRUD_Workflows
from utils.ip_utils import IPUtils
from constants.infra_constants import HOST_PUBLIC_NETWORK, HOST_PUBLIC_SUBNET

def weight_to_prob(ip_weight_list):
    def sum_of_weights():
        tmp = 0
        for i in range(len(ip_weight_list)):
            tmp += ip_weight_list[i]['weight']
        return tmp
        
    print(ip_weight_list)
    result = []
    for i in range(len(ip_weight_list)):
        perc =  ip_weight_list[i]['weight'] / sum_of_weights()
        ip_weight_list[i]['weight'] = 0
        result.append({ip_weight_list[i]['ip']:perc})
    return(result)

class VMController:
    @staticmethod 
    def define(db, vm_id: ObjectId | str):
        if isinstance(vm_id, str):
            vm_id = ObjectId(vm_id)
        vm = VM.find_by_id(db, vm_id)
        if vm.state == VMState.STARTING or vm.state == VMState.UPDATING or vm.state == VMState.DELETING:
            return False
        try:
            if vm.state == VMState.ERROR:
                VMController.undefine(db, vm_id)
                # vm.undefine()
            elif vm.state != VMState.UNDEFINED:
                print("VM is already defined")
                return False
                
            vm.state = VMState.STARTING
            vm.save(db)
            
            interfaces = db.interface.find({'instance_id': vm.get_id()})
            print(type(interfaces))
            formatted_interface = []
            for interface in interfaces:
                print(interface)
                tmp = Interface.from_dict(interface)
                
                print("tmp:", tmp)
                tmp1 = db.subnet.find_one({'_id': tmp.subnet_id})
                print("tmp1:", tmp1)
                conn_nw = Subnet.from_dict(tmp1)
                out = {}
                out['network_name'] = conn_nw.network_name
                out['iface_name'] = tmp.interface_name 
                out['ipaddress'] = tmp.ip_address + "/" + conn_nw.get_host_mask()
                out['dhcp'] = False
                if tmp.gateway:
                    out['gateway'] = tmp.gateway
                formatted_interface.append(out)
            if vm.load_balancer is not None and len(vm.load_balancer) > 0:
                out = {}
                out['network_name'] = HOST_PUBLIC_NETWORK
                out['iface_name'] = 'ep1'
                lb_key = [i for i in vm.load_balancer.keys()][0]
                lb:LoadBalancer = LoadBalancer.find_by_id(db, vm.load_balancer[lb_key])
                out['ipaddress'] = lb.lb_ip + "/" + HOST_PUBLIC_SUBNET.split('/')[1]
                cal_ip_weights = weight_to_prob(lb.target_group)
                out_tenant_ips = {}
                for i in range(len(cal_ip_weights)):
                    for ip, weight in cal_ip_weights[i].items():
                        out_tenant_ips[ip] = weight
                out['tenantIps'] = out_tenant_ips
                formatted_interface.append(out)
            print(formatted_interface)
            print(vm.name, vm.vCPU, vm.vMem, vm.disk_size, formatted_interface)
            if vm.isRouterVM:
                ansible_func = ROUTER_CRUD_Workflows.run_ansible_playbook_for_router_definition
            else:
                ansible_func = VM_CRUD_Workflows.run_ansible_playbook_for_vm_definition
            print(vm.name, vm.vCPU, vm.vMem, vm.disk_size, formatted_interface)
            if ansible_func(vm.name, vm.vCPU, vm.vMem, vm.disk_size, formatted_interface):
                vm.state = VMState.DEFINED
                vm.save(db)
            else:
                vm.state = VMState.ERROR
                vm.save(db)
        except Exception:
            if vm.state != VMState.ERROR:
                vm.state = VMState.ERROR
                vm.save(db)
            traceback.print_exc()
            
    @staticmethod
    def undefine(db, vm: ObjectId | str):
        if isinstance(vm, str):
            vm = ObjectId(vm)
        vm = VM.find_by_id(db, vm)
        if vm.state == VMState.STARTING or vm.state == VMState.UPDATING or vm.state == VMState.DELETING:
            # VM is changing state already
            return False
        try:
            if vm.state == VMState.UNDEFINED:
                print("VM is already undefined")
                # VM is already defined
                return True
            
            vm.state = VMState.DELETING
            vm.save(db)

            print("Undefine called")
            if vm.isRouterVM:
                ansible_func = ROUTER_CRUD_Workflows.run_ansible_playbook_for_router_deletion
            else:
                ansible_func = VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion
            if ansible_func(vm.name):
                vm.state = VMState.UNDEFINED
                vm.save(db)
            else:
                vm.state = VMState.ERROR
                vm.save(db)

        except Exception:
            print("Exception")
            if vm.state != VMState.ERROR:
                vm.state = VMState.ERROR
                vm.save(db)
            traceback.print_exc()
            
    @staticmethod
    def start(db, vm_id: ObjectId | str):
        if isinstance(vm_id, str):
            vm_id = ObjectId(vm_id)
        vm: VM = VM.find_by_id(db, vm_id)
        if vm.state == VMState.UPDATING or vm.state == VMState.STARTING or vm.state == VMState.DELETING:
            return False
        try:
            if vm.state == VMState.ERROR:
                VMController.undefine(db, vm_id)
                VMController.define(db, vm_id)
            elif vm.state == VMState.UNDEFINED:
                VMController.define(db, vm_id)
            elif vm.state == VMState.RUNNING:
                print("VM is already running")
                return True
            vm.state = VMState.UPDATING
            vm.save(db)
            if vm.isRouterVM:
                ansible_func = ROUTER_CRUD_Workflows.run_ansible_playbook_for_router_start
            else:
                ansible_func = VM_CRUD_Workflows.run_ansible_playbook_for_vm_start
            if ansible_func(vm.name):
                vm.state = VMState.RUNNING
                vm.save(db)
            else:
                vm.state = VMState.ERROR
                vm.save(db)
        except Exception:
            if vm.state != VMState.ERROR:
                vm.state = VMState.ERROR
                vm.save(db)
            traceback.print_exc()
    
    @staticmethod
    def connect_to_network(db,
                           vpc: ObjectId | str,
                           subnet: ObjectId | str,
                           vm: ObjectId | str,
                           is_gateway = False,
                           ip_address: str | None = None,
                           default = False,
                           load_balancing_interface = False,
                           load_balancer_name = None
                           ):
        if isinstance(vpc, str):
            vpc = ObjectId(vpc)
        vpc = VPC.find_by_id(db, vpc)
        if isinstance(subnet, str):
            subnet = ObjectId(subnet)
        subnet: Subnet = Subnet.find_by_id(db, subnet)
        if isinstance(vm, str):
            vm = ObjectId(vm)
        vm:VM = VM.find_by_id(db, vm)
        
        # Check if subnet is already connected
        exists = db.interface.find_one({'subnet_id': subnet.get_id(), 'instance_id': vm.get_id()})
        if exists:
            return True
        
        if not subnet:
            raise Exception("Subnet not found")
        
        vm_status = vm.state
        VMController.undefine(db, vpc.routerVM)
        
        subnet_nw = subnet.get_ipobj()
        if ip_address is None:
            sb_nw = subnet_nw.hosts()
            if is_gateway:
                ip_address = subnet_nw[1]
            else:
                used_ips: set[IPv4Address] = {IPv4Address(item['ip_address']) for item in db.interface.find({"subnet_id": subnet.get_id()})}
                used_ips.add(subnet_nw[1])
                i = 2
                while True:
                    ip_address = next(sb_nw, i)
                    if ip_address not in used_ips:
                        break
                    else:
                        i = random.randrange(10)
            ip_address = str(ip_address)
        
        mac_address = IPUtils.generate_unique_mac(db)
        network_mask = subnet.get_host_mask()
        gateway = str(subnet_nw[1]) if default else None
        interface_name = Interface.get_next_interface_name(db, instance_id = vm.get_id(), is_default = default, load_balancing_interface = load_balancing_interface)
        
        lb = None
        if load_balancing_interface:
            lb = LoadBalancer(load_balancer_name, vpc.get_id(), type=LBType.IAAS.name, lb_instance=vm.get_id(), target_group=[])
            lb.save(db)
        
        net_interface = Interface(ip_address, mac_address, network_mask, gateway, vm.get_id(), subnet.get_id(), interface_name, load_balancer=lb)
        net_interface.save(db)
        vm.interfaces.append(net_interface.get_id())
        vm.save(db)

        if vm_status == VMState.RUNNING:
            VMController.start(db, vpc.routerVM)
        elif vm_status == VMState.DEFINED:
            VMController.define(db, vpc.routerVM)

        return net_interface
    
    @staticmethod
    def create_load_balancer(db, vpc: VPC | ObjectId,  vm_id: ObjectId | str, lb_name: str, lb_ip: str, lb_type: str):
        try:
            if isinstance(vm_id, str):
                vm_id = ObjectId(vm_id)
            if isinstance(vpc, ObjectId):
                vpc = VPC.find_by_id(db, vpc)
                
                
            vm = VM.find_by_id(db, vm_id)
            if vm.load_balancer and vm.load_balancer.get(lb_name, None):
                print("Load Balancer App already exists")
                return True
            lb = LoadBalancer(lb_name,
                              vpc.get_id(),
                              type = lb_type,
                              lb_instance = vm.get_id(),
                              target_group = [],
                              lb_ip = lb_ip,
                              )
            lb.save(db)
            if vm.load_balancer is None:
                vm.load_balancer = {}
            vm.load_balancer[lb.name] = lb.get_id()
            vm.save(db)
            return True
        except:
            traceback.print_exc()
            return False
        
    @staticmethod
    def rm_load_balancer(db, vpc: VPC | ObjectId, vm_id: ObjectId | str, lb_name: str):
        try:
            if isinstance(vm_id, str):
                vm_id = ObjectId(vm_id)
            if isinstance(vpc, ObjectId):
                vpc = VPC.find_by_id(db, vpc)
            vm = VM.find_by_id(db, vm_id)
            
            lb_id = vm.load_balancer.get(lb_name, None)
            if lb_id is None:
                return True
            del vm.load_balancer[lb_name]
            lb: LoadBalancer = LoadBalancer.find_by_id(db, lb_id)
            if len(vm.load_balancer) == 0:
                vm.load_balancer = None
            vm.save(db)
            lb.delete(db)
            return True
        except:
            traceback.print_exc()
            return False
    
    @staticmethod
    def add_lb_ip_target(db, vm_id: ObjectId | str, lb_name: str, ip_target: str, weight: int = 1):
        if isinstance(vm_id, str):
            vm_id = ObjectId(vm_id)
        vm: VM = VM.find_by_id(db, vm_id)
        # vm_state = vm.state
        lb_id = vm.load_balancer.get(lb_name, None)
        if lb_id is None:
            raise Exception("Load balancer not found")
        lb: LoadBalancer = LoadBalancer.find_by_id(db, lb_id)
        lb.add_ip_address(db, ip_target, weight)
        lb.save(db)
    
    @staticmethod
    def rm_lb_ip_target(db, vm_id: ObjectId | str, lb_name: str, ip_target):
        if isinstance(vm_id, str):
            vm_id = ObjectId(vm_id)
        vm: VM = VM.find_by_id(db, vm_id)
        
        lb_id = vm.load_balancer.get(lb_name, None)
        if lb_id is None:
            raise Exception("Load balancer not found")
        lb: LoadBalancer = LoadBalancer.find_by_id(lb_id)
        lb.rm_ip_address(db, ip_target)
        lb.save(db)
    
    @staticmethod
    def disconnect_from_network(db, vm_id: ObjectId | str, subnet_id: ObjectId | str):
        if isinstance(subnet_id, str):
            subnet_id = ObjectId(subnet_id)
        if isinstance(vm_id, str):
            vm_id = ObjectId(vm_id)
        vm = VM.find_by_id(vm_id)
        data = db.interface.find_one({'instance_id': vm_id, 'subnet_id': subnet_id})
        if data:
            interface = Interface.from_dict(data)
            vm.interfaces.remove(interface.get_id())
            interface.delete(db)
            vm.save(db)
            
    @staticmethod
    def get_ip_by_vm_name_and_cidr(db, vm_name: str, cidr: str):
        pass
            
        
    @staticmethod
    def shutdown():
        pass
    
    @staticmethod
    def pause():
        pass
    
    @staticmethod
    def resume():
        pass
            