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
    SUSPENDED = 6       # VM is suspended
    UPDATING = 7        # VM is updating (unstable)
    ERROR = 8           # VM ran into an unfixable error
    DELETING = 9        # VM is getting deleted

class VM:
    def __init__(self, name, vCPU, vMem, disk_size, interfaces: List[str] | None = None, isRouterVM = False, state = VMState.UNDEFINED.name, _id = None):
        self._id = _id
        self.name = name
        self.vCPU = vCPU
        self.vMem = vMem
        self.disk_size = disk_size
        self.status = VMState[state]
        self.interfaces = interfaces or []
        self.isRouterVM = isRouterVM 

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

    def connect_to_network(self, db, subnet_id: ObjectId | str, is_gateway = False, ip_address: str | None = None, default = False, load_balancing_interface = False):
        if isinstance(subnet_id, str):
            subnet_id = ObjectId(subnet_id)
        subnet = Subnet.find_by_id(db, subnet_id)
        if subnet:
            subnet_network = subnet.get_ipobj()
            
            if ip_address is None:
                sb_nw = subnet_network.hosts()
                if is_gateway:
                    ip_address = next(sb_nw)
                else:
                    # fetch all ips currently in use
                    used_ips: set[IPv4Address] = {IPv4Address(item['ip_address']) for item in db.interface.find({"subnet_id": subnet.get_id()})}
                    used_ips.add(IPv4Address(str(next(sb_nw))))
                    i = 2
                    while True:
                        ip_address = next(sb_nw, i)
                        if ip_address not in used_ips:
                            break
                        else:
                            i = random.choice(range(1,10))
                            ip_address = next(sb_nw, i)
                    # available_ips = [ip for ip in [next(subnet_network.hosts(),2)] if ip not in used_ips]
                    
                ip_address = str(ip_address)
                
            # generate a unique mac
            mac_address = IPUtils.generate_unique_mac(db)

            # network_mask
            network_mask = subnet.get_host_mask()
            # gatway
            gateway = str(next(subnet_network.hosts())) if default else None
            #interface name
            interface_name = Interface.get_next_interface_name(db, instance_id = self._id, is_default = default, load_balancing_interface = load_balancing_interface)
            print(interface_name, self.name, subnet.network_name, ip_address, gateway)
            # create an interface obj
            net_interface = Interface(ip_address, mac_address, network_mask, gateway, self._id, subnet_id, interface_name)
            net_interface.save(db)
            self.interfaces.append(net_interface.get_id())
            self.save(db)
            
            return net_interface
            
    def disconnect_from_network(self, db, subnet_id: ObjectId | str):
        if isinstance(subnet_id, str):
            subnet_id = ObjectId(subnet_id)
        interface = db.interface.find({'instance_id': self._id, 'subnet_id': subnet_id})
        if interface:
            self.interfaces.remove(interface.get_id())
            interface.delete(db)
            self.save(db)

    def list_interfaces(self, db):
        # for dat in db.interface.find({'_id': {'$in': self.interfaces}}):
        #     print(dat)
            # Interface.from_()
        return [Interface.from_dict(data) for data in db.interface.find({'_id': {'$in': self.interfaces}})]

    def save(self, db):
        if self._id is None:
            obj = db.vm.insert_one(self.to_dict())
            inserted_id = obj.inserted_id
            self._id = inserted_id
        else:
            db.vm.update_one({'_id': self._id}, {'$set': self.to_dict()})
        return self
    
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
                "isRouterVM": self.isRouterVM,
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
                  data['isRouterVM'],
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
