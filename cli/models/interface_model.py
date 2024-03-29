from utils.utils import Utils
from bson.objectid import ObjectId


class Interface:
    def __init__(self, ip_address, mac_address, network_mask, gateway, instance_id, subnet_id, interface_name, _id = None):
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.network_mask = network_mask
        self.gateway = gateway
        self.instance_id = instance_id
        self.subnet_id = subnet_id
        self.interface_name = interface_name
        self._id = _id

    def save(self, db):
        if self._id is None:
            obj = db.interface.insert_one(self.to_dict())
            inserted_id = obj.inserted_id
            self._id = inserted_id
        else:
            db.interface.update_one({'_id': self._id}, {'$set': self.to_dict()})
        return self
    
    def get_id(self):
        return self._id

    def to_dict(self):
        return { "ip_address": self.ip_address,
                 "mac_address": self.mac_address,
                 "network_mask": self.network_mask,
                 "gateway": self.gateway,
                 "instance_id": self.instance_id,
                 "subnet_id": self.subnet_id,
                 "interface_name": self.interface_name,
                 }
    
    def delete(self, db):
        if self._id is not None:
            db.interface.delete_one({'_id': self._id})
            self._id = None

    def json(self):
        Utils.print_json(self.to_dict())

    @staticmethod
    def from_dict(data):
        return Interface( data['ip_address'],
                          data['mac_address'],
                          data['network_mask'], 
                          data['gateway'], 
                          data['instance_id'], 
                          data['subnet_id'], 
                          data['interface_name'], 
                          _id = data['_id']
                          )
    
    @staticmethod
    def find_by_id(db, id):
        data = db.interface.find_one({'_id': Utils.id(id)})
        if data:
            return Interface.from_dict(data)
        return None
    
    @staticmethod
    def find_by_instance_and_network(db, instance_id: str | ObjectId, subnet_id):
        if isinstance(instance_id, str):
            instance_id = ObjectId(instance_id)
        if isinstance(subnet_id, str):
            subnet_id = ObjectId(subnet_id)
        data = db.interface.find_one({'instance_id': instance_id, 'subnet_id': subnet_id})
        if data:
            return Interface.from_dict(data)
    
    @staticmethod
    def get_next_interface_name(db, instance_id: str | ObjectId, load_balancing_interface = False, is_default = False) -> str:
        # 'enp{num}s0' num is interface number
        # num = 0 for default connction
        # num = 1 for other subnets and so on
        # num = 2 ...
        
        # lb balancer naming ep1, ep2, ep3 ......
        # self.interface_name = 'enp1s0'
        DEFAULT_INTERFACE_NAME = 'enp1s0'
        if isinstance(instance_id, str):
            instance_id = ObjectId(instance_id)
        if is_default:
            interface_count = db.interface.count_documents({"instance_id": instance_id, 'interface_name': 'enp0s0'})
            if 0 == interface_count:
                return DEFAULT_INTERFACE_NAME
            else:
                raise Exception('cannot more than one default interface')
        
        else:
            if not load_balancing_interface:
                default_offset = db.interface.count_documents({"instance_id": instance_id, 'interface_name': DEFAULT_INTERFACE_NAME})
                interface_num = db.interface.count_documents({"instance_id": instance_id, 'interface_name':{'$regex':'^enp'}}) + 2 - default_offset
                return f"enp{interface_num}s0"
            else:
                interface_num = db.interface.count_documents({"instance_id": instance_id, 'interface_name':{'$regex':'^ep'}}) + 1
                return f"ep{interface_num}"
        
        
