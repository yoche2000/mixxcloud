from commands import VM_CRUD_Workflows

"""
vm_name = "ProjectGuestVM-3"
vcpu = 2
mem = 2048
disk_size = "12G"
interfaces = [
    {
        "network_name": "L2",
        "iface_name": "enp1s0",
        "ipaddress": "192.168.1.106/24",
        "dhcp": False,
        "gateway": "192.168.1.1",
    }
]
"""

vm_name = "Public-Internet-Client"
vcpu = 2
mem = 2048
disk_size = "12G"
interfaces = [
    {
        "network_name": "host-public-network",
        "iface_name": "enp1s0",
        "ipaddress": "10.10.10.100/24"
    }
]

VM_CRUD_Workflows.run_ansible_playbook_for_vm_definition(vm_name, vcpu, mem, disk_size, interfaces)
VM_CRUD_Workflows.run_ansible_playbook_for_vm_start(vm_name)