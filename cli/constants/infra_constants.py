HOST_NAT_NETWORK = "pvtnw"
HOST_NAT_SUBNET = "172.16.0.0/12"
HOST_NAT_BR_NAME = "pvt"

HOST_PUBLIC_NETWORK = "pubnw"
HOST_PUBLIC_SUBNET = "10.10.10.0/24"
HOST_PUBLIC_BR_NAME = "pub"

ROUTER_VM_VCPU = 2
ROUTER_VM_MEM = 2048
ROUTER_VM_DISK_SIZE = 10

VRRP_CONFIG_FILE = '/home/vmadm/mixxcloud/card/docker_hadb.csv'


REGION_MAPPING = {"east": "odd", "west": 'even'}