from enum import Enum
from bson.objectid import ObjectId
from ipaddress import IPv4Address
import traceback

from utils.utils import Utils

class LBType(Enum):
    IAAS = 1
    VM = 2

class LoadBalancer:
    def __init__(self, 
                 name: str,
                 vpc_id: str,
                 type = LBType.IAAS.name,
                 instance_east : ObjectId | None = None,
                 instance_west : ObjectId | None = None,
                 lb_ip : str | None = None,
                 target_group = [],
                 _id = None,
                 ):
        self.name = name
        self.type = LBType[type]
        self.instance_east = instance_east
        self.instance_west = instance_west
        self.lb_ip = lb_ip
        self.target_group = target_group
        self.vpc_id = vpc_id
        self._id = _id
        
    def add_ip_address(self, db, ip_address: str, weight: int):
        try:
            _ = IPv4Address(ip_address)
            weight = int(weight)
            for target in self.target_group:
                if target['ip'] == ip_address:
                    raise Exception('ip already exists')
            self.target_group.append({'ip':ip_address, "weight": weight})
            self.save(db)
            return True
        except Exception:
            traceback.print_exc()
            print("invalid ip address")
            return False
    
    def rm_ip_address(self, db, ip_address: str):
        try:
            _ = IPv4Address(ip_address)
            for target in self.target_group:
                if target['ip'] == ip_address:
                    self.target_group.remove(target)
                    break
            self.save(db)
            return True
        except:
            traceback.print_exc()
            print("invalid ip address")
            return False
            
    def save(self, db):
        if self._id is None:
            obj = db.loadbalancer.insert_one(self.to_dict())
            inserted_id = obj.inserted_id
            self._id = inserted_id
        else:
            db.loadbalancer.update_one({'_id': self._id}, {'$set': self.to_dict()})
        return self
    
    def get_id(self):
        return self._id

    def to_dict(self):
        return {
                "name": self.name,
                "type": self.type.name,
                "instance_east": self.instance_east,
                "instance_west": self.instance_west,
                "lb_ip": self.lb_ip,
                "target_group": self.target_group,
                "vpc_id": self.vpc_id,
                }
    
    def delete(self, db):
        if self._id is not None:
            db.loadbalancer.delete_one({'_id': self._id})
            self._id = None

    def json(self):
        Utils.print_json(self.to_dict())

    @staticmethod
    def from_dict(data):
        if data is None: return
        return LoadBalancer(data['name'], data['vpc_id'], type= data['type'], lb_ip = data['lb_ip'], target_group= data['target_group'],  _id = data['_id'], instance_east = data['instance_east'], instance_west = data['instance_west'],)
    
    @staticmethod
    def find_by_name(db, name):
        data = db.loadbalancer.find_one({'name': name})
        if data:
            return LoadBalancer.from_dict(data)
        return None

    @staticmethod
    def find_by_id(db, id: ObjectId | str):
        if isinstance(id, str):
            id = ObjectId(id)
        data = db.loadbalancer.find_one({'_id': id})
        if data:
            return LoadBalancer.from_dict(data)
        return None


    
class LBRules:
    def __init__(self) -> None:
        pass