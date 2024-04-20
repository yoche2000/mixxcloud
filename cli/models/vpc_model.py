# #vpc
# {
#     'name':'vpc1',
#     'region': "us-east1",
#     'subnets': [subnet_id]
#     '_subnets': Subnet()
# }


from enum import Enum
from typing import List
from .subnet_model import Subnet
from .vm_model import VM
from .interface_model import Interface
from utils.utils import Utils
from constants.infra_constants import HOST_NAT_NETWORK
from bson.objectid import ObjectId

class VPCStatus(Enum):
    UNDEFINED = 1
    CREATING = 2
    RUNNING = 3
    UPDATING = 4
    DELETING = 5
    ERROR = 6

class VPC:
    def __init__(self, 
                 name, 
                 subnets = None, 
                 container_east = None,
                 container_west = None,
                 status = VPCStatus.UNDEFINED.name,
                 lbs = {},
                 lb_running = False,
                 _id = None
                 ):
        self._id = _id
        self.name = name
        self.subnets: List[str] = subnets or []
        self.container_east = container_east
        self.container_west = container_west
        self.status = VPCStatus[status]
        self.lbs = lbs
        self.lb_running = lb_running

    def list_subnets(self, db) -> List[Subnet]:
        return list(db.subnet.find({'_id': {'$in': self.subnets}}))

    def get_router(self, region: str) -> ObjectId:
        if region == 'east':
            return self.container_east
        else:
            return self.container_west

    def save(self, db):
        if self._id is None:
            obj = db.vpc.insert_one(self.to_dict())
            inserted_id = obj.inserted_id
            self._id = inserted_id
        else:
            db.vpc.update_one({'_id': self._id}, {'$set': self.to_dict()})
        return self
    
    def get_id(self):
        return self._id

    def to_dict(self):
        return {
                "name": self.name,
                "subnets": self.subnets,
                'container_east': self.container_east,
                'container_west': self.container_west,
                "status": self.status.name,
                "lbs": self.lbs,
                "lb_running": self.lb_running,
               }
    
    def delete(self, db):
        if self._id is not None:
            for subnet in self.list_subnets():
                subnet.delete(db)
            db.vpc.delete_one({'_id': self._id})
            self._id = None

    def json(self):
        Utils.print_json(self.to_dict())

    @staticmethod
    def from_dict(data):
        if data is None: return
        # print(data)
        return VPC(data['name'], 
                   data['subnets'], 
                   container_east=data['container_east'],
                   container_west=data['container_west'], 
                   status=data['status'],
                   lbs = data['lbs'],
                   lb_running = data['lb_running'],
                   _id = data['_id'], 
                   )

    @staticmethod
    def find_by_name(db, name):
        data = db.vpc.find_one({'name':name})
        if data:
            return VPC.from_dict(data)
        return None
    
    @staticmethod
    def find_by_id(db, id):
        data = db.vpc.find_one({'_id': Utils.id(id)})
        if data:
            return VPC.from_dict(data)
        return None
    
    @staticmethod
    def unique_name(db, name):
        data = db.vpc.find_one({'name':name})
        return False if data else True
