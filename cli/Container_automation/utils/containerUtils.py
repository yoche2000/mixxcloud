from southbound_constants import Files
import yaml

class containerConfiguration:
    @staticmethod
    def createContainerVarsFiles(container_name,container_image):
        """
        Creates a YAML file for container configuration.
        - container_name (str): Name of the container.
        - container_image (str): Image for the container.

        Sample:
        container_name: C2
        container_image: vpcrouter
        """

        data = {
            "container_name": container_name,
            "container_image": container_image
        }
        
        print(f"Preparing to create the container Configuration File: {Files.CONTAINER_VARS_FILE_PATH}")
        file_path = f"{Files.CONTAINER_VARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Container Configuration File Is Created...")

    @staticmethod
    def createVPCToPVTVarsFile(container_name, bridge_name, ip_address, gateway_vpc):
        data = {
            "container_name": container_name,
            "bridge_name": bridge_name,
            "ip_address": ip_address,
            "gateway_vpc": gateway_vpc
        }
        file_path = f"{Files.VETH_VARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Veth Configuration File Is Created...")
    
    @staticmethod
    def createVPCToPUBVarsFile(container_name, bridge_name):
        data = {
            "container_name": container_name,
            "bridge_name": bridge_name
        }
        file_path = f"{Files.VETH_VARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Veth Configuration File Is Created...")
    
    @staticmethod
    def createLBToPUBVarsFile(container_name, bridge_name):
        data = {
            "container_name": container_name,
            "bridge_name": bridge_name
        }
        file_path = f"{Files.VETH_VARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Veth Configuration File Is Created...")
    
    @staticmethod
    def createLBToSUBNETVarsFile(container_name, bridge_name, ip_address, gateway_lb):
        data = {
            "container_name": container_name,
            "bridge_name": bridge_name,
            "ip_address": ip_address,
            "gateway_lb": gateway_lb
        }
        file_path = f"{Files.VETH_VARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Veth Configuration File Is Created...")

    @staticmethod
    def createContainerSubnetVarsFile(container_name, subnet_name, subnet, gateway, vni_id, local_ip, remote_ip):
        data = {
            "container_name": container_name,
            "subnet_name": subnet_name,
            "subnet": subnet,
            "gateway": gateway,
            "vni_id": vni_id,
            "local_ip": local_ip,
            "remote_ip": remote_ip
        }
        file_path = f"{Files.SUBNET_VARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Subnet Configuration File Is Created...")
    
    @staticmethod
    def createLBVarsFile(container_name, lb_ip, tenantIps):
        data = {
            "container_name": container_name,
            "lb_ip": lb_ip,
            "tenantIps": tenantIps
        }
        file_path = f"{Files.VETH_VARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"LB Configuration File Is Created...")
    
    @staticmethod
    def createVMVarsFile(vm_name, vcpu, mem, disk_size, interfaces):
        data = {
            "vms": [
                {
                    "vm_name": vm_name,
                    "vcpu": vcpu,
                    "mem": mem,
                    "disk_size": disk_size,
                    "interfaces": interfaces,
                }
            ]
        }
        
        print(f"Preparing to create the VM Configuration File: {Files.VM_VARS_FILE_PATH}")
        file_path = f"{Files.VMVARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"VM Configuration File Is Created...")