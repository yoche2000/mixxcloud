import subprocess
import json
from utilities import VMUtils

class VM_CRUD_Workflows:
    def run_ansible_playbook_for_vm_creation(userID, vmName, vCPU, memory, diskSize, netWorkName, interfaceName, dhcpStatus, gatewayIP = None):
        """
        TODO:
        1. Add Validation for Network, Interface and DHCP Status by Querying the database to check if the network exists.
        """
        vms_config = VMUtils.setVMArguments(vmName, vCPU, memory, diskSize, netWorkName, interfaceName, dhcpStatus, gatewayIP)
        # Serialize the VM configuration to a JSON string
        extra_vars = json.dumps({"vms": vms_config})
        
        # Command to execute ansible-playbook with the JSON string as extra-vars
        command = ["ansible-playbook", "ansible/create-vm.yml", "--extra-vars", extra_vars]
        
        # Run the command and capture output
        process = subprocess.run(command, capture_output=True, text=True)
        
        # Print the output and any errors
        print(process.stdout)
        if process.stderr:
            print("Error:", process.stderr)
        
        # TODO: Populate the below return value in database.Ex: UserID field should have the VM ID in the table.
        # VM ID = UserID + VMName + vpcName
        # return f"{userID}-{vmName}-{}"
    
    def run_ansible_playbook_for_router_vm_creation(vmName, vCPU = 2, memory = 2048, diskSize = "10G", netWorkName = "PublicNetworkOfHost", interfaceName = "PublicNetworkOfHostInterface", dhcpStatus = True, gatewayIP = "172.16.0.1"):
        # HostNetwork, HostInterface and GatewayIP should be given from Deepak/ThomasWorkflows
        vms_config = VMUtils.setVMArguments(vmName, vCPU, memory, diskSize, netWorkName, interfaceName, dhcpStatus, gatewayIP)
        extra_vars = json.dumps({"vms": vms_config})
            
        # Command to execute ansible-playbook with the JSON string as extra-vars
        command = ["ansible-playbook", "ansible/create-vm.yml", "--extra-vars", extra_vars]
        
        # Run the command and capture output
        process = subprocess.run(command, capture_output=True, text=True)
        
        # Print the output and any errors
        print(process.stdout)
        if process.stderr:
            print("Error:", process.stderr)

    def run_ansible_playbook_for_removing_subnet_to_vm(vmName, interfaceNameToBeRemoved):
        # HostNetwork, HostInterface and GatewayIP should be given from Deepak/ThomasWorkflows
        vms_config = VMUtils.setArgumentsForRemoveInterfaceToVM(vmName, interfaceNameToBeRemoved)
        extra_vars = json.dumps({"vms": vms_config})
        print(extra_vars)
        # Command to execute ansible-playbook with the JSON string as extra-vars
        command = ["ansible-playbook", "ansible/remove-interface.yml", "--extra-vars", extra_vars]
        
        # Run the command and capture output
        process = subprocess.run(command, capture_output=True, text=True)
        
        # Print the output and any errors
        print(process.stdout)
        if process.stderr:
            print("Error:", process.stderr)
    
    @staticmethod
    def run_ansible_playbook_for_removing_subnet_to_vm(vmName):
        command = ["ansible-playbook", "ansible/destroy-vm.yml", '-e', f"vm_name={vmName}"]
        process = subprocess.run(command, capture_output=True, text=True)
        
        # Print the output and any errors
        print(process.stdout)
        if process.stderr:
            print("Error:", process.stderr)

# Assuming vms_config is defined as shown above
# Workflows.run_ansible_playbook_for_vm_creation("HW3_GuestVM1111111", 2, 2048, "10G", "Internet", "enp1s0", True, "192.168.1.1")
# VM_CRUD_Workflows.run_ansible_playbook_for_removing_subnet_to_vm("HW3_GuestVM1111111","enp1s0")
