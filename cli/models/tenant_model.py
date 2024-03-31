from typing import List
from .vpc_model import VPC
from utils.utils import Utils

class Tenant():
    def __init__(self, name: str, vpcs: List[str] | List[VPC] | None = None, _id=None):
        self._id = _id
        self.name = name
        self.vpcs = vpcs or []

    def create_vpc(self, db, name, region):
        vpc = self.get_vpc_by_name(db, name)
        if not vpc:
            vpc = VPC(name, region)
            vpc.save(db)
            vpc.create_router(db)
            self.vpcs.append(vpc.get_id())
            self.save(db)
        return vpc

    def get_vpc_by_name(self, db, name):
        data = db.vpc.find_one({'name': name})
        if data:
            return VPC.from_dict(data)

    def save(self, db):
        if self._id is None:
            obj = db['tenant'].insert_one(self.to_dict())
            inserted_id = obj.inserted_id
            self._id = inserted_id
        else:
            db['tenant'].update_one({'_id': self._id}, {'$set': self.to_dict()})
        return self
    
    def get_id(self):
        return self._id

    def to_dict(self):
        return {"name": self.name, "vpcs": self.vpcs}
    
    def delete(self, db):
        if self._id is not None:
            for vpc in self.vpcs:
                tmp=VPC.find_by_id(db,vpc)
                tmp.delete(db)
            db.tenant.delete_one({'_id': self._id})
            self._id = None
    
    def json(self):
        Utils.print_json(self.to_dict())

    @staticmethod
    def from_dict(data):
        return Tenant(data['name'], data['vpcs'], _id = data['_id'])

    @staticmethod
    def find_by_name(db, name):
        data = db['tenant'].find_one({'name':name})
        #print("Data",data)
        if data:
            return Tenant.from_dict(data)
        return None

    @staticmethod
    def find_by_id(db, id):
        data = db.tenant.find_one({'_id': Utils.id(id)})
        if data:
            return Tenant.from_dict(data)
        return None
