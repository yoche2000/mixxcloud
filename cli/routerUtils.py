from southbound_constants import Files
import yaml

class RouterConfiguration:
    # TODO: 
    # 1. Implement a function for creating the dictionary for interfaces after fetching the details from database.
    # 2. Implement Shell Files for NAT Rules and Load Balancer Rules.

    @staticmethod
    def createRouterVarsFile(vm_name, vcpu, mem, disk_size, interfaces):
        """
        Creates a YAML file for VM configuration.
        - vm_name (str): Name of the VM.
        - vcpu (int): Number of virtual CPUs.
        - mem (int): Memory in MB.
        - disk_size (str): Disk size in GB with 'G' suffix.
        - interfaces (list): List of dictionaries, each representing a network interface.

        Sample:
        vms:
        -   vm_name: RouterVM
            vcpu: 2
            mem: 2048
            disk_size: 12G
            interfaces: 
            -   network_name: "host-nat-network"
                iface_name: enp1s0
                ipaddress: 172.16.222.2/24
                dhcp: false
                gateway: 172.16.222.1
            -   network_name: "L2"
                iface_name: enp2s0
                dhcp: false
                ipaddress: 192.168.1.1/24 
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
        
        print(f"Preparing to create the Router Configuration File: {Files.ROUTERVARS_FILE_PATH.value}")
        file_path = f"{Files.ROUTERVARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Router Configuration File Is Created...")
    
    # @staticmethod
    # def createNATRulesFile():

    # @staticmethod
    # def createLoadBalancerRulesFile():


# Test Case:
vm_name = "RouterVM"
vcpu = 2
mem = 2048
disk_size = "12G"
interfaces = [
    {
        "network_name": "host-nat-network",
        "iface_name": "enp1s0",
        "ipaddress": "172.16.222.2/24",
        "dhcp": False,
        "gateway": "172.16.222.1",
    },
    {
        "network_name": "L2",
        "iface_name": "enp2s0",
        "ipaddress": "192.168.1.1/24",
    }
]
# RouterConfiguration.createRouterVarsFile(vm_name, vcpu, mem, disk_size, interfaces)


        
