from commands import ROUTER_CRUD_Workflows


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
        "network_name": "host-public-network",
        "iface_name": "enp3s0",
        "ipaddress": "10.10.10.2/24",
    }
]

ROUTER_CRUD_Workflows.run_ansible_playbook_for_router_definition(vm_name, vcpu, mem, disk_size, interfaces)
ROUTER_CRUD_Workflows.run_ansible_playbook_for_router_start(vm_name)