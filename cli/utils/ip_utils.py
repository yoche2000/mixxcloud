from ipaddress import IPv4Address, ip_network
import random
from bson.objectid import ObjectId
from models.subnet_model import Subnet
from constants.infra_constants import REGION_MAPPING

class IPUtils:
    @staticmethod
    def generate_mac():
        # Create a MAC address with the first octet even (unicast & globally unique)
        # by ensuring the second character is one of the even hexadecimal digits.
        mac = [random.choice('02468AEC')] + [random.choice('0123456789ABCDEF') for _ in range(11)]
        
        # Format the MAC address as XX:XX:XX:XX:XX:XX
        mac_address = ':'.join(''.join(mac[i:i+2]) for i in range(0, 12, 2))
        
        return mac_address
    
    @staticmethod
    def generate_unique_mac(db):
        mac_address = IPUtils.generate_mac()
        while True:
            data = db.interface.find_one({"mac_address": mac_address})
            if data:
                mac_address = IPUtils.generate_mac()
            else:
                return mac_address
    
    @staticmethod
    def get_unique_ip_from_region(db, sb_id: ObjectId, region: str, is_gateway: bool = False ):
        if region not in ['even', 'odd']:
            region = REGION_MAPPING[region]
        print(region)
        sbnw = Subnet.find_by_id(db, sb_id)
        subnet_nw = ip_network(sbnw.cidr)
        sb_nw = subnet_nw.hosts()
        if is_gateway:
            if region == 'odd':
                ip_address = subnet_nw[1]
            else:
                ip_address = subnet_nw[2]
        else:
            used_ips: set[IPv4Address] = {IPv4Address(item['ip_address']) for item in db.interface.find({"subnet_id": sb_id})}
            used_ips.add(subnet_nw[1])
            used_ips.add(subnet_nw[2])
            i = 3
            while True:
                ip_address = next(sb_nw, i)
                temp = str(ip_address)
                temp = int(temp.split('.')[3])
                # temp = 2
                if region == 'even':
                    if temp%2 != 0:
                        ip_address = next(sb_nw)
                if region == 'odd':
                    if temp%2 != 1:
                        ip_address = next(sb_nw)
                        
                # if region == 'east' and temp % 2 != 1:
                #     ip_address = next(sb_nw)
                # elif region == 'west' and temp % 2 == 0: 
                #     ip_address = next(sb_nw)
                if ip_address not in used_ips:
                    break
                else:
                    i = random.randrange(10)
        ip_address = str(ip_address)
        return ip_address
    
    @staticmethod
    def get_default_subnet_gateway(db, sb_id: ObjectId, region: str):
        return IPUtils.get_unique_ip_from_region(db, sb_id, region, is_gateway = True)
    
    @staticmethod
    def get_gateway(subnet):
        pass
    
    @staticmethod
    def get_network_mask(subnet):
        pass