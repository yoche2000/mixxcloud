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

def weight_to_prob(ip_weight_list):
    result = []
    for ip in ip_weight_list.keys():
        perc =  ip_weight_list[ip] / sum(ip_weight_list.values())
        ip_list[ip] = 0
        result.append({ip:perc})
    return(result)

'''
## weight_to_prob example
ip_list = {"192.168.1.1":7,
           '192.168.1.2':3,
           '192.168.1.3':2}
print(weight_to_prob(ip_list))
'''
