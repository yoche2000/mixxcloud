from enum import Enum
from bson.objectid import ObjectId
from utils.utils import Utils

class ContainerStatus(Enum):
    UNDEFINED = 1
    RUNNING = 2
    UPDATING = 3
    STOPPED = 4
    DELETING = 5
    ERROR = 6

class Container:
    def __init__(self, name, image, region, vCPU, mem, interfaces = [], status = ContainerStatus.UNDEFINED.name, _id= None, vpc_id = None):
        self._id = _id
        self.name = name
        self.image = image
        self.region = region
        self.interfaces = interfaces
        self.vCPU = vCPU
        self.mem = mem
        self.status = ContainerStatus[status]
        self.vpc_id = vpc_id

    def save(self, db):
        if self._id is None:
            obj = db.container.insert_one(self.to_dict())
            inserted_id = obj.inserted_id
            self._id = inserted_id
        else:
            db.container.update_one({'_id': self._id}, {'$set': self.to_dict()})
        return self
    
    def get_id(self):
        return self._id

    def to_dict(self):
        return { 
                 "name": self.name,
                 "image": self.image,
                 "vCPU": self.vCPU,
                 "mem": self.mem,
                 "interfaces": self.interfaces,
                 "region": self.region,
                 "status": self.status.name,
                 "vpc_id": self.vpc_id,
                 }
    
    def delete(self, db):
        if self._id is not None:
            db.container.delete_one({'_id': self._id})
            self._id = None

    def json(self):
        Utils.print_json(self.to_dict())

    @staticmethod
    def from_dict(data):
        return Container( data['name'], 
                          data['image'], 
                          data['region'], 
                          data['vCPU'], 
                          data['mem'], 
                          interfaces = data['interfaces'],
                          _id = data['_id'],
                          status=data['status'],
                          vpc_id=data['vpc_id'],
                          )
    
    @staticmethod
    def find_by_id(db, id):
        data = db.container.find_one({'_id': ObjectId(id)})
        if data:
            return Container.from_dict(data)
        return None
    
    @staticmethod
    def find_by_name(db, name):
        data = db.container.find_one({'name': name})
        if data:
            return Container.from_dict(data)
        return None