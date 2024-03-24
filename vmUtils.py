from constants import Files
import yaml

class VMConfiguration:
    # TODO: Implement a method for creating the dictionary for interfaces after fetching the details from database.
    @staticmethod
    def createVMVarsFile(vm_name, vcpu, mem, disk_size, interfaces):
        """
        Creates a YAML file for VM configuration.
        - vm_name (str): Name of the VM.
        - vcpu (int): Number of virtual CPUs.
        - mem (int): Memory in MB.
        - disk_size (str): Disk size in GB with 'G' suffix.
        - interfaces (list): List of dictionaries, each representing a network interface.

        Sample:
        vms:
        - vm_name: ProjectGuestVM2
            vcpu: 2
            mem: 2048
            disk_size: 12G
            interfaces: 
              - network_name: "L2"
                iface_name: enp1s0
                ipaddress: 192.168.1.102/24
                dhcp: false
                gateway: 192.168.1.1
        """

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
        
        print(f"Preparing to create the VM Configuration File: {Files.VMVARS_FILE_PATH}")
        file_path = f"{Files.VMVARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"VM Configuration File Is Created...")


# Test Case:
vm_name = "ProjectGuestVM2"
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
# VMConfiguration.createVMVarsFile(vm_name, vcpu, mem, disk_size, interfaces)


        
