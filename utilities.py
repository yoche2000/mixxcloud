class VMUtils:
    @staticmethod
    def setVMArguments(vmName, vCPU, memory, diskSize, netWorkName, interfaceName, dhcpStatus, gatewayIP=None):
        """
        @params: Configurations related to VM
        @returns: List of Dictionary for 
        Sample VM Config:
        vms:
        - vm_name: HW3_GuestVM1
            vcpu: 2
            mem: 2048
            disk_size: 12G
            interfaces: 
            - network_name: "{{ networks['Internet'].network_name }}"
            iface_name: enp1s0
            dhcp: true
            gateway: "{{ networks['Internet'].gateway }}"
        """
        vms_config = [
            {
                "vm_name": vmName,
                "vcpu": vCPU,
                "mem": memory,
                "disk_size": diskSize,
                "interfaces": [
                    {
                        "network_name": netWorkName,
                        "iface_name": interfaceName,
                        "dhcp": dhcpStatus
                    }
                ]
            }
        ]

        if gatewayIP != None:
            vms_config["interfaces"][0]["gateway"] = gatewayIP

        return vms_config

    @staticmethod
    def setArgumentsForRemoveInterfaceToVM(vmName, interfaceNameToBeRemoved):
        # TODO: Fetch the VM Config of this VM from the Database. Let's say it is vms_config.
        vms_config = [
            {
                "vm_name": "HW3_GuestVM1111111",
                "vcpu": 2,
                "mem": 2048,
                "disk_size": "10G",
                "interfaces": [
                    {
                        "network_name": "Internet",
                        "iface_name": "enp1s0",
                        "dhcp": True
                    }
                ]
            }
        ]
        print("Before:",vms_config)
        for vm_config in vms_config:
            vm_config["interfaces"] = [
                iface for iface in vm_config["interfaces"]
                if iface.get("iface_name") != interfaceNameToBeRemoved
            ]
        print("After:",vms_config)
        return vms_config
        

