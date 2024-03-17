import ipaddress
import math

def check_subnet(cidr):
    ## if subnet in vpc, return error
    if '/' not in cidr  or int(cidr.split('/')[1]) >30:
        raise ValueError("Network Size must be larger than /30")
    n_cidr = ipaddress.ip_network(cidr)
    return n_cidr

def subnet_supernet(vpc, subnet):
    vpc = ipaddress.ip_network(vpc)
    subnet = ipaddress.ip_network(subnet)
    flag = subnet[1] in vpc and subnet[-1] in vpc
    ## False means subnet is not within VPC/address block range
    return flag

