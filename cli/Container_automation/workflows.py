import subprocess
import json
from southbound_utils import Commands
from Container_automation.utils.containerUtils import containerConfiguration
import traceback

class LB_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_lb_rules(container_name, lb_ip, lb_snat_ip, tenantIps, region = None):
        '''
        this is for adding load balancer rules
        '''
        try:
            print(f"LB rules for {container_name} has been triggered..")
            containerConfiguration.createLBVarsFile(container_name, lb_ip, lb_snat_ip, tenantIps)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_rules_LB.yml"]
            if region is not None:
                command.extend(['-l', region])
            Commands.run_command(command)
            print(f"LB rules for {container_name} has been completed..")
            return True
        except Exception as error:
            print(f"Failure in LB rules Creation. More details: {error}")
            return False
    
    @staticmethod
    def run_ansible_playbook_for_lb_rules_deletion(container_name, iaas, region = None):
        try:
            print(f"LB rules Deletion for {container_name}  has been triggered..")
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/delete_rules_LB.yml", "-e", f"container_name={container_name}", "-e", f"iaas={iaas}"]
            if region is not None:
                command.extend(['-l', region])
            Commands.run_command(command)
            print(f"LB rules Deletion for {container_name} has been completed..")
        except Exception as e:
            print(f"LB rules deletion for  {container_name} has a failure..")
            traceback.print_exc()
            return False
        return True
    
class VMContainer_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_vmcontainer_creation(container_name,container_image,vcpu,mem):
        try:
            print(f"VMContainer creation for {container_name} has been triggered..")
            containerConfiguration.createVMVarsFile(container_name,container_image,vcpu,mem)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_vm.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"VMContainer creation for {container_name} has been completed..")
            return True
        except Exception as error:
            print(f"Failure VMContainer creation for {container_name}. More details: {error}")
            return False

class Subnet_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_subnet_creation(container_name, subnet_name, subnet, gateway, vni_id, local_ip, remote_ip):
        '''
        this is for creating subnet inside vpc
        '''
        try:
            print(f"Subent Creation for {container_name} has been triggered..")
            containerConfiguration.createContainerSubnetVarsFile(container_name, subnet_name, subnet, gateway, vni_id, local_ip, remote_ip)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_subnet.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"Subent Creation for {container_name} has been completed..")
            return True
        except Exception as error:
            print(f"Failure in Subent Creation. More details: {error}")
            return False

    @staticmethod
    def run_ansible_playbook_for_subnet_deletion(container_name, subnet_name, vni_id):
        try:
            print(f"Subnet Deletion for {subnet_name} in {container_name} has been triggered..")
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "ansible/delete_subnet.yml", "-e", f"container_name={container_name}", "-e", f"subnet_name={subnet_name}", "-e", f"vni_id={vni_id}", '-l', 'even']
            Commands.run_command(command)
            print(f"Container Deletion for {subnet_name} in {container_name} has been completed..")
        except Exception as e:
            print(f"Container deletion for {subnet_name} in {container_name} has a failure..")
            traceback.print_exc()
            return False
        return True


class Container_CRUD_Workflows:
    @staticmethod
    def run_ansible_playbook_for_container_creation(container_name, container_image, region, vcpu = None, mem = None):
        try:
            print(f"Container Creation for {container_name} has been triggered..")
            containerConfiguration.createContainerVarsFiles(container_name, container_image, vcpu, mem)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_container.yml"]
            if region is not None:
                command.extend(['-l', region])
            Commands.run_command(command)
            print(f"Container Creation for {container_name} has been completed..")
            return True
        except Exception as error:
            print(f"Failure in Container Creation. More details: {error}")
            return False
    
    @staticmethod
    def run_ansible_playbook_for_container_deletion(container_name, region = None):
        try:
            print(f"Container Deletion for {container_name} has been triggered..")
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/delete_container.yml", "-e", f"container_name={container_name}", '-l', 'even']
            if region is not None:
                command.extend(['-l', region])
            Commands.run_command(command)
            print(f"Container Deletion for {container_name} has been completed..")
        except Exception as e:
            print(f"Container deletion for {container_name} has a failure..")
            traceback.print_exc()
            return False
        return True

    @staticmethod
    def run_ansible_playbook_for_container_to_sb_connection(container_name, bridge_name, ip_address, default_ip, region, is_nat):
        # testing
        # print(container_name, bridge_name, ip_address, default_ip, region, is_nat)
        try:
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been triggered..")
            containerConfiguration.createContainerVarsForSubnetConnection(container_name, bridge_name, ip_address, default_ip, is_nat)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_veth_container_bridge.yml"]
            if region is not None:
                command.extend(['-l', region])
            print(command)
            Commands.run_command(command)
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been completed..")
            return True
        except Exception as error:
            traceback.print_exc()
            print(f"Veth pair Creation for {container_name} and  {bridge_name}. More details: {error}")
            return False
        
    @staticmethod
    def run_ansible_playbook_for_container_subnet_creation(container_name, subnet_name, subnet, gateway, vni_id, local_ip, remote_ip, region = None):
        try:
            print(f"Subnet Creation started for {container_name} and  {subnet_name} has been triggered..")
            containerConfiguration.createContainerSubnetVarsFile(container_name, subnet_name, subnet, gateway, vni_id, local_ip, remote_ip)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_subnet.yml"]
            if region is not None:
                command.extend(['-l', region])
            print(command)
            Commands.run_command(command)
            print(f"Subnet Creation for {container_name} and  {subnet_name} has been completed..")
            return True
        except Exception as error:
            traceback.print_exc()
            print(f"Subnet Creation for {container_name} and  {subnet_name}. More details: {error}")
            return False
        

    @staticmethod
    def run_ansible_playbook_for_vpc_to_pvt(container_name, bridge_name, ip_address, gateway_vpc):
        '''
        this is for container to act as vpc router, container to pvt bridge veth pair
        '''
        try:
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been triggered..")
            containerConfiguration.createVPCToPVTVarsFile(container_name, bridge_name, ip_address, gateway_vpc)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_veth_container_bridge.yml"]
            print(command)
            Commands.run_command(command)
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been completed..")
            return True
        except Exception as error:
            traceback.print_exc()
            print(f"Veth pair Creation for {container_name} and  {bridge_name}. More details: {error}")
            return False
    
    @staticmethod
    def run_ansible_playbook_for_vpc_to_pub(container_name, bridge_name):
        '''
        this is for vpc router to act as LB, IAAS approach, vpc to pub bridge veth pair
        '''
        try:
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been triggered..")
            containerConfiguration.createVPCToPVTVarsFile(container_name, bridge_name)
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
            containerConfiguration.createVPCToPVTVarsFile(container_name, bridge_name)
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
        this is for vmcontainer to subnet as well
        '''
        
        try:
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been triggered..")
            containerConfiguration.createVPCToPVTVarsFile(container_name, bridge_name, ip_address, gateway_lb)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/create_veth_container_bridge.yml",  '-l', 'odd']
            Commands.run_command(command)
            print(f"Veth pair Creation for {container_name} and  {bridge_name} has been completed..")
            return True
        except Exception as error:
            print(f"Veth pair Creation for {container_name} and  {bridge_name}. More details: {error}")
            return False
