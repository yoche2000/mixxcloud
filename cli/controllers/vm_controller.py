from ipaddress import IPv4Address
import random
import traceback
from bson.objectid import ObjectId
from models.interface_model import Interface
from models.vm_model import VM, VMState
from models.subnet_model import Subnet
from commands import VM_CRUD_Workflows, ROUTER_CRUD_Workflows
from utils.ip_utils import IPUtils

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
    def connect_to_network(db, subnet: ObjectId | str, vm: ObjectId | str, is_gateway = False, ip_address: str | None = None, default = False, load_balancing_interface = False):
        if isinstance(subnet, str):
            subnet = ObjectId(subnet)
        subnet: Subnet = Subnet.find_by_id(db, subnet)
        if isinstance(vm, str):
            vm = ObjectId(vm)
        vm = VM.find_by_id(db, vm)
        if not subnet:
            raise Exception("Subnet not found")
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
        net_interface = Interface(ip_address, mac_address, network_mask, gateway, vm.get_id(), subnet.get_id(), interface_name)
        net_interface.save(db)
        vm.interfaces.append(net_interface.get_id())
        vm.save(db)

        return net_interface
    
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
    def shutdown():
        pass
    
    @staticmethod
    def pause():
        pass
    
    @staticmethod
    def resume():
        pass
            