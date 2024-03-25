from pprint import pprint
from typing import List 
from bson.objectid import ObjectId
from ipaddress import ip_network, IPv4Network
import traceback

# from models.subnet_model import Subnet

class Utils:
    @staticmethod
    def print_json(obj):
        pprint(obj)

    @staticmethod
    def id(id):
        return ObjectId(id)
        
    # @staticmethod
    # def ip_pvt_and_not_overlapping(ip_ranges: List[Subnet]):
    #     for i in ip_ranges:
    #         if not ip_ranges.is_private():
    #             return False
    #     sbs: List[IPv4Network] = [sb.get_ipobj() for sb in ip_ranges]
    #     for i in range(len(sbs)):
    #         for j in range(i+1, len(sbs)):
    #             if sbs[i].overlaps(sbs[j]):
    #                 return True
    #     return False
