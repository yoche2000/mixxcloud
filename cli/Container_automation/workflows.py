import subprocess
import json
from southbound_utils import Commands
from utils import containerUtils
import traceback

class LB_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_lb_rules(container_name, lb_ip, tenantIps):
        '''
        this is for adding load balancer rules
        '''
        try:
            print(f"LB rules for {container_name} has been triggered..")
            containerUtils.containerConfiguration.createLBVarsFile(container_name, lb_ip, tenantIps)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_rules_LB.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"LB rules for {container_name} has been completed..")
            return True
        except Exception as error:
            print(f"Failure in LB rules Creation. More details: {error}")
            return False
    
class VM_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_vm_creation(vmName, vCPU, memory, diskSize, interfaces):
        try:
            print(f"VM creation for {vmName} has been triggered..")
            containerUtils.containerConfiguration.createVMVarsFile(vmName, vCPU, memory, diskSize, interfaces)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_vm.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"VM creation for {vmName} has been completed..")
            return True
        except Exception as error:
            print(f"Failure VM creation for {vmName}. More details: {error}")
            return False

class Subnet_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_subnet_creation(container_name, subnet_name, subnet, gateway, vni_id, local_ip, remote_ip):
        '''
        this is for creating subnet inside vpc
        '''
        try:
            print(f"Subent Creation for {container_name} has been triggered..")
            containerUtils.containerConfiguration.createContainerSubnetVarsFile(container_name, subnet_name, subnet, gateway, vni_id, local_ip, remote_ip)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_subnet.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"Subent Creation for {container_name} has been completed..")
            return True
        except Exception as error:
            print(f"Failure in Subent Creation. More details: {error}")
            return False

    @staticmethod
    def run_ansible_playbook_for_subnet_deletion(nw_name, br_name):
        pass


class Container_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_container_creation(container_name, container_image):
        try:
            print(f"Container Creation for {container_name} has been triggered..")
            containerUtils.containerConfiguration.createContainerVarsFiles(container_name, container_image)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_container.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"Container Creation for {container_name} has been completed..")
            return True
        except Exception as error:
            print(f"Failure in Container Creation. More details: {error}")
            return False

    @staticmethod
    def run_ansible_playbook_for_vpc_to_pvt(container_name, bridge_name, ip_address, gateway_vpc):
        '''
        this is for container to act as vpc router, container to pvt bridge veth pair
        '''
        try:
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been triggered..")
            containerUtils.containerConfiguration.createVPCToPVTVarsFile(container_name, bridge_name, ip_address, gateway_vpc)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_veth_container_bridge.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been completed..")
            return True
        except Exception as error:
            print(f"Veth pair Creation for {container_name} and  {bridge_name}. More details: {error}")
            return False
    
    @staticmethod
    def run_ansible_playbook_for_vpc_to_pub(container_name, bridge_name):
        '''
        this is for vpc router to act as LB, IAAS approach, vpc to pub bridge veth pair
        '''
        try:
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been triggered..")
            containerUtils.containerConfiguration.createVPCToPVTVarsFile(container_name, bridge_name)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_veth_container_bridge.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been completed..")
            return True
        except Exception as error:
            print(f"Veth pair Creation for {container_name} and  {bridge_name}. More details: {error}")
            return False
    
    @staticmethod
    def run_ansible_playbook_for_lb_to_pub(container_name, bridge_name):
        '''
        this is for container to act as LB, LBAAS approach, container to pub bridge veth pair, LB container is not yet attached to subnet 
        '''
        try:
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been triggered..")
            containerUtils.containerConfiguration.createVPCToPVTVarsFile(container_name, bridge_name)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_veth_container_bridge.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been completed..")
            return True
        except Exception as error:
            print(f"Veth pair Creation for {container_name} and  {bridge_name}. More details: {error}")
            return False
    
    @staticmethod
    def run_ansible_playbook_for_lb_to_subnet(container_name, bridge_name, ip_address, gateway_lb):
        '''
        this is when for LB to connect to a subnet, LBAAS approach, container to subnet bridge veth pair
        '''
        try:
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been triggered..")
            containerUtils.containerConfiguration.createVPCToPVTVarsFile(container_name, bridge_name, ip_address, gateway_lb)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_veth_container_bridge.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been completed..")
            return True
        except Exception as error:
            print(f"Veth pair Creation for {container_name} and  {bridge_name}. More details: {error}")
            return False
