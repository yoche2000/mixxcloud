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
from controllers.vm_controller import VMController
import traceback

class VMState(Enum):
    UNDEFINED = 1       # No resources created/allocated
    STARTING = 2        # Allocating Resources
    DEFINED = 3         # Resources allocated, first boot not done
    RUNNING = 4         # VM is runniing
    SHUTDOWN = 5        # VM is shutdown
    PAUSED = 6          # VM is paused 
    SUSPENDED = 7       # VM is suspended
    UPDATING = 8        # VM is updating (unstable)
    ERROR = 9           # VM ran into an unfixable error
    DELETING = 10       # VM is getting deleted

def format_disk_size(disk_size):
    try:
        if 'G' in disk_size:
            return disk_size
        int(disk_size)
    except:
        return f"{disk_size}G"

class VM:
    def __init__(self, name, vCPU, vMem, disk_size, interfaces: List[str] | None = None, isRouterVM = False, state = VMState.UNDEFINED.name, _id = None):
        self._id = _id
        self.name = name
        self.vCPU = vCPU
        self.vMem = vMem
        self.disk_size = format_disk_size(disk_size)
        self.state = VMState[state]
        self.interfaces = interfaces or []
        self.isRouterVM = isRouterVM 
        self.load_balancer_info = None

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
            
    def define(self, db):
        if self.state == VMState.STARTING or self.state == VMState.UPDATING or self.state == VMState.DELETING:
            # VM is changing state already
            return False
        try:
            if self.state == VMState.ERROR:
                # self.undefine()
                pass
            elif self.state != VMState.UNDEFINED:
                print("VM is already defined")
                # VM is already defined
                return False
                
            
            self.state = VMState.STARTING
            self.save(db)
            def success():
                self.state = VMState.DEFINED
                self.save(db)
            def failure():
                self.state = VMState.ERROR
                self.save(db)
            
            interfaces = db.interface.find({'instance_id': self._id})
            formatted_interface = []
            for interface in interfaces:
                tmp = Interface.from_dict(interface)
                print(tmp.json())
                tmp1 = db.subnet.find_one({'_id': tmp.subnet_id})
                print(tmp1)
                conn_nw = Subnet.from_dict(tmp1)
                out = {}
                out['network_name'] = conn_nw.network_name
                out['iface_name'] = tmp.interface_name
                out['ipaddress'] = tmp.ip_address
                out['dhcp'] = False
                if tmp.gateway:
                    out['gateway'] = tmp.gateway
                formatted_interface.append(out)
            print(formatted_interface)
            
            VMController.create(self.name, self.vCPU, self.vMem, self.disk_size, formatted_interface, success=success, failure=failure)
        except Exception:
            if self.state != VMState.ERROR:
                failure()
            traceback.print_exc()
        
    def undefine(self, db):
        if self.state == VMState.STARTING or self.state == VMState.UPDATING or self.state == VMState.DELETING:
            # VM is changing state already
            return False
        try:
            if self.state == VMState.UNDEFINED:
                print("VM is already undefined")
                # VM is already defined
                return True
            
            self.state = VMState.DELETING
            self.save(db)
            def success():
                self.state = VMState.UNDEFINED
                self.save(db)
            def failure():
                print("Failure was called")
                self.state = VMState.ERROR
                self.save(db)
                print("Trying to destroy")
            print("Undefine called")
            VMController.destroy(self.name, success=success, failure=failure)
        except Exception:
            print("Exception")
            if self.state != VMState.ERROR:
                failure()
            traceback.print_exc()
    
    def start(self, db):
        if self.state == VMState.UPDATING or self.state == VMState.STARTING or self.start == VMState.DELETING:
            return False
        try:
            if self.state == VMState.ERROR:
                self.undefine(db)
                self.define(db)
            elif self.state == VMState.UNDEFINED:
                self.define(db)
            elif self.state == VMState.RUNNING:
                print("VM is already running")
                return True
            self.state = VMState.UPDATING
            self.save(db)
            def success():
                self.state = VMState.RUNNING
                self.save(db)
            def failure():
                self.state = VMState.ERROR
                self.save(db)
            VMController.start(self.name, success=success, failure=failure)
        except Exception:
            if self.state != VMState.ERROR:
                failure()
            traceback.print_exc()

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
                "interfaces": self.interfaces,
                "isRouterVM": self.isRouterVM,
                "state": self.state.name,
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
                  state=data['state'],
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
