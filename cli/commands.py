import subprocess
import json
from vmUtils import VMConfiguration
from southbound_utils import Commands
from routerUtils import RouterConfiguration

class VM_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_vm_creation(vmName, vCPU, memory, diskSize, interfaces):
        print(f"VM Creation for {vmName} has been triggered..")
        VMConfiguration.createVMVarsFile(vmName, vCPU, memory, diskSize, interfaces)
        command = ["ansible-playbook", "-i", "ansible/hosts", "ansible/create-vm.yml"]
        Commands.run_command(command)
        print(f"VM Creation for {vmName} has been completed..")
    
    @staticmethod
    def run_ansible_playbook_for_vm_definition(vmName, vCPU, memory, diskSize, interfaces):
        try:
            print(f"VM Definition for {vmName} has been triggered..")
            VMConfiguration.createVMVarsFile(vmName, vCPU, memory, diskSize, interfaces)
            command = ["ansible-playbook", "-i", "ansible/hosts", "ansible/create-vm-definition.yml"]
            Commands.run_command(command)
            print(f"VM Definition for {vmName} has been completed..")
        except Exception as error:
            print(f"VM Definition for {vmName} has a failure..")
            print(f"More Details: {error}")
            return False
        return True
    
    @staticmethod
    def run_ansible_playbook_for_vm_start(vmName):
        try:
            print(f"VM Start for {vmName} has been triggered..")
            command = ["ansible-playbook", "-i", "ansible/hosts", "ansible/create-vm-start.yml","-e",f"vm_name={vmName}"]
            Commands.run_command(command)
            print(f"VM Start for {vmName} has been completed..")
        except Exception as error:
            print(f"VM Start for {vmName} has a failure..")
            print(f"More Details: {error}")
            return False
        return True

    @staticmethod
    def run_ansible_playbook_for_vm_deletion(vmName):
        print(f"VM Deletion for {vmName} has been triggered..")
        command = ["ansible-playbook", "-i", "ansible/hosts", "ansible/destroy-vm.yml", "-e", f"vm_name={vmName}"]
        Commands.run_command(command)
        print(f"VM Deletion for {vmName} has been completed..")
    
    @staticmethod
    def run_ansible_playbook_to_detach_vm_from_network(vmName, networkName):
        # Thought: Delete and Create can also be done.
        print(f"VM Detach for {vmName} from Network {networkName} has been triggered..")
        command = ["ansible-playbook", "-i", "ansible/hosts", "ansible/detach-vm.yml", "-e", f"vm_name={vmName}", "-e", f"network_name={networkName}"]
        Commands.run_command(command)
        print(f"VM Detach for {vmName} from Network {networkName} has been completed..")
    
    @staticmethod
    def run_ansible_playbook_to_attach_vm_to_network(vmName, vCPU, memory, diskSize, interfaces):
        print(f"Attaching VM {vmName} to New Networks has been triggered..")
        VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion(vmName)
        VM_CRUD_Workflows.run_ansible_playbook_for_vm_creation(vmName, vCPU, memory, diskSize, interfaces)
        print(f"VM {vmName} is attached to New Networks, and the workflow has been completed..")

class ROUTER_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_router_creation(vmName, vCPU, memory, diskSize, interfaces):
        print(f"Router Creation for {vmName} has been triggered..")
        RouterConfiguration.createRouterVarsFile(vmName, vCPU, memory, diskSize, interfaces)
        command = ["ansible-playbook", "-i", "ansible/hosts", "ansible/create-vm-router.yml"]
        Commands.run_command(command)
        print(f"Router Creation for {vmName} has been completed..")
    
    @staticmethod
    def run_ansible_playbook_for_attaching_subnet_to_vpc(vmName, vCPU, memory, diskSize, interfaces):
        print(f"Attaching New Subnets To The VPC..Stablizing Router..")
        VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion(vmName)
        ROUTER_CRUD_Workflows.run_ansible_playbook_for_router_creation(vmName, vCPU, memory, diskSize, interfaces)
        print(f"Router is Stablized, subnets have been attached..")
    
    @staticmethod
    def run_ansible_playbook_for_router_definition(vmName, vCPU, memory, diskSize, interfaces):
        try:
            print(f"Router Definition for {vmName} has been triggered..")
            RouterConfiguration.createRouterVarsFile(vmName, vCPU, memory, diskSize, interfaces)
            command = ["ansible-playbook", "-i", "ansible/hosts", "ansible/create-vm-router-definition.yml"]
            Commands.run_command(command)
            print(f"Router Definition for {vmName} has been completed..")
        except Exception as error:
            print(f"Router Definition for {vmName} has a failure..")
            print(f"More Details: {error}")
            return False
        return True

    @staticmethod
    def run_ansible_playbook_for_router_start(vmName):
        try:
            print(f"Router Start for {vmName} has been triggered..")
            command = ["ansible-playbook", "-i", "ansible/hosts", "ansible/create-vm-router-start.yml","-e",f"vm_name={vmName}"]
            Commands.run_command(command)
            print(f"Router Start for {vmName} has been completed..")
        except Exception as error:
            print(f"Router Start for {vmName} has a failure..")
            print(f"More Details: {error}")
            return False
        return True

    @staticmethod
    def run_ansible_playbook_for_router_deletion(vmName):
        print(f"Router Deletion for {vmName} has been triggered..")
        command = ["ansible-playbook", "-i", "ansible/hosts", "ansible/destroy-vm.yml", "-e", f"vm_name={vmName}"]
        Commands.run_command(command)
        print(f"Router Deletion for {vmName} has been completed..")



# Testing:
"""
1: Create VPC => Router VM Creation

vm_name = "RouterVM"
vcpu = 2
mem = 2048
disk_size = "12G"
interfaces = [
    {
        "network_name": "host-nat-network",
        "iface_name": "enp1s0",
        "ipaddress": "172.16.222.2/12",
        "dhcp": False,
        "gateway": "172.16.0.1",
    },
    {
        "network_name": "L2",
        "iface_name": "enp2s0",
        "ipaddress": "192.168.1.1/24",
    }
]

ROUTER_CRUD_Workflows.run_ansible_playbook_for_router_creation(vm_name, vcpu, mem, disk_size, interfaces)
"""

"""
Create Router => Definition and Start

vm_name = "RouterVM"
vcpu = 2
mem = 2048
disk_size = "12G"
interfaces = [
    {
        "network_name": "host-nat-network",
        "iface_name": "enp1s0",
        "ipaddress": "172.16.222.2/12",
        "dhcp": False,
        "gateway": "172.16.0.1",
    },
    {
        "network_name": "L2",
        "iface_name": "enp2s0",
        "ipaddress": "192.168.1.1/24",
    }
]

ROUTER_CRUD_Workflows.run_ansible_playbook_for_router_definition(vm_name, vcpu, mem, disk_size, interfaces)
ROUTER_CRUD_Workflows.run_ansible_playbook_for_router_start(vm_name)
"""


"""
2. VM Creation

vm_name = "ProjectGuestVM"
vcpu = 2
mem = 2048
disk_size = "12G"
interfaces = [
    {
        "network_name": "L2",
        "iface_name": "enp1s0",
        "ipaddress": "192.168.1.102/24",
        "dhcp": False,
        "gateway": "192.168.1.1",
    }
]
VM_CRUD_Workflows.run_ansible_playbook_for_vm_creation(vm_name, vcpu, mem, disk_size, interfaces)
"""

"""
2. VM Creation - Define
"""
vm_name = "ProjectGuestVM-3"
vcpu = 2
mem = 2048
disk_size = "12G"
interfaces = [
    {
        "network_name": "L2",
        "iface_name": "enp1s0",
        "ipaddress": "192.168.1.105/24",
        "dhcp": False,
        "gateway": "192.168.1.1",
    }
]

VM_CRUD_Workflows.run_ansible_playbook_for_vm_definition(vm_name, vcpu, mem, disk_size, interfaces)
VM_CRUD_Workflows.run_ansible_playbook_for_vm_start(vm_name)


"""
3. Deletion of VM

VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion("RouterVM")
"""

"""
4. VM Update: Attaching Subnets

vm_name = "ProjectGuestVM"
vcpu = 2
mem = 2048
disk_size = "12G"
interfaces = [
    {
        "network_name": "L2",
        "iface_name": "enp1s0",
        "ipaddress": "192.168.1.102/24",
        "dhcp": False,
        "gateway": "192.168.1.1",
    },
    {
        "network_name": "L2-V1",
        "iface_name": "enp2s0",
        "ipaddress": "192.168.2.102/24",
        "dhcp": False,
        "gateway": "192.168.2.1",
    }
]
VM_CRUD_Workflows.run_ansible_playbook_to_attach_vm_to_network(vm_name, vcpu, mem, disk_size, interfaces)
"""

"""
5. VM Update: Detaching Subnets

vm_name = "ProjectGuestVM"
networkName = "L2-V1"
VM_CRUD_Workflows.run_ansible_playbook_to_detach_vm_from_network(vm_name,networkName)
"""

"""
6. Router Update: Attaching New Subnets

vm_name = "RouterVM"
vcpu = 2
mem = 2048
disk_size = "12G"
interfaces = [
    {
        "network_name": "host-nat-network",
        "iface_name": "enp1s0",
        "ipaddress": "172.16.222.2/12",
        "dhcp": False,
        "gateway": "172.16.0.1",
    },
    {
        "network_name": "L2",
        "iface_name": "enp2s0",
        "ipaddress": "192.168.1.1/24",
    },
    {
        "network_name": "L2-V1",
        "iface_name": "enp3s0",
        "ipaddress": "192.168.2.1/24",
    }
]
ROUTER_CRUD_Workflows.run_ansible_playbook_for_attaching_subnet_to_vpc(vm_name, vcpu, mem, disk_size, interfaces)
"""