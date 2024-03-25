# #instance
# {
#     'name': 'vm_name',
#     'vCPU': 1,
#     'vMem': 2,
#     'diskSize': 10,
#     'networks' : [
#         {
#             'network_id': 'id1',
#             'network_ip' : 'ip',
#             'network_mask': 'mask',
#             'slot_id': 'id',
#         }
#     ]
# }
from enum import Enum
from typing import List
from .interface_model import Interface
from .subnet_model import Subnet
from utils.utils import Utils
from utils.ip_utils import IPUtils
from bson.objectid import ObjectId
from ipaddress import IPv4Address
import random

class VMState(Enum):
    UNDEFINED = 1       # No resources created/allocated
    DEFINED = 2         # Resources allocated, first boot not done
    RUNNING = 3         # VM is runniing
    SHUTDOWN = 4        # VM is shutdown
    PAUSED = 5          # VM is paused 
    SUSPENDED = 6       # VM is suspende

class VM:
    def __init__(self, name, vCPU, vMem, disk_size, interfaces: List[str] | None = None, state = VMState.UNDEFINED.name, _id = None):
        self._id = _id
        self.name = name
        self.vCPU = vCPU
        self.vMem = vMem
        self.disk_size = disk_size
        self.status = VMState[state]
        self.interfaces = interfaces or []

    def add_interface(self, db, ip_address, mac_address, network_mask, gateway):
        if VMState.UNDEFINED:
            interface = Interface(ip_address, mac_address, network_mask, gateway, self._id)
            interface.save(db)
            self.interfaces.append(interface.get_id())
        else:
            # Logic for when adding interface when vm is in any other state
            pass

    def remove_interface(self, db, interface_id) -> bool:
        if VMState.UNDEFINED:
            interface = Interface.find_by_id(db, interface_id)
            if interface is None:
                return False
            self.interfaces.remove(interface.get_id())
            interface.delete(db)

    def connect_to_network(self, db, subnet_id: ObjectId | str, ip_address: str | None = None, default = False):
        if isinstance(subnet_id, str):
            subnet_id = ObjectId(subnet_id)
        subnet = Subnet.find_by_id(subnet_id)
        if subnet:
            subnet_network = subnet.get_ipobj()
            
            if ip_address is None:
                # fetch all ips currently in use
                used_ips: List[str] = [item['ip_address'] for item in db.interface.find({"subnet_id": subnet.get_id()})]
                available_ips = [ip for ip in next(subnet_network.hosts(),2) if ip not in [IPv4Address(ip4) for ip4 in used_ips]]
                
                # choose a unique ip addr
                ip_address = str(random.choice(available_ips))
                
            # generate a unique mac
            mac_address = IPUtils.generate_unique_mac(db)

            # network_mask
            network_mask = subnet.get_host_mask()
            # gatway
            gateway = str(next(subnet_network.hosts())) if default else None
            # create an interface obj
            net_interface = Interface(ip_address, mac_address, network_mask, gateway, self._id, subnet_id)
            net_interface.save(db)
            self.interfaces.append(net_interface.get_id())
            self.save(db)
            
    def disconnect_from_network(self, db, subnet_id: ObjectId | str):
        if isinstance(subnet_id, str):
            subnet_id = ObjectId(subnet_id)
        interface = db.interface.find({'instance_id': self._id, 'subnet_id': subnet_id})
        if interface:
            self.interfaces.remove(interface.get_id())
            interface.delete(db)
            self.save(db)

    def list_interfaces(self, db):
        for dat in db.interface.find({'_id': {'$in': self.interfaces}}):
            print(dat)
            # Interface.from_()
        return [Interface.from_dict(data) for data in db.interface.find({'_id': {'$in': self.interfaces}})]

    def save(self, db):
        if self._id is None:
            obj = db.vm.insert_one(self.to_dict())
            inserted_id = obj.inserted_id
            self._id = inserted_id
        else:
            db.vm.update_one({'_id': self._id}, {'$set': self.to_dict()})
    
    def get_id(self):
        return self._id

    def to_dict(self):
        return { 
                "name": self.name,
                "vCPU": self.vCPU,
                "vMem": self.vMem,
                "disk_size": self.disk_size,
                "status": self.status.name,
                "interfaces": self.interfaces,
               }
    
    def delete(self, db):
        if self._id is not None:
            db.vm.delete_one({'_id': self._id})
            self._id = None

    def json(self):
        Utils.print_json(self.to_dict())

    @staticmethod
    def from_dict(data):
        return VM(data['name'], 
                  data['vCPU'], 
                  data['vMem'], 
                  data['disk_size'], 
                  data['interfaces'],
                  state=data['status'],
                  _id = data['_id'])

    @staticmethod
    def find_by_name(db, name):
        data = db.vm.find_one({'name':name})
        if data:
            return VM.from_dict(data)
        return None
    
    @staticmethod
    def find_by_id(db, id):
        data = db.vm.find_one({'_id': Utils.id(id)})
        if data:
            return VM.from_dict(data)
        return None
