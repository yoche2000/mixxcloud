from utils.utils import Utils
from bson.objectid import ObjectId


class Interface:
    def __init__(self, ip_address, mac_address, network_mask, gateway, instance_id, subnet_id, _id = None):
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.network_mask = network_mask
        self.gateway = gateway
        self.instance_id = instance_id
        self.subnet_id = subnet_id
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
