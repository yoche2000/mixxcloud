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


class VPCStatus(Enum):
    UNDEFINED = 1
    CREATING = 2
    RUNNING = 3
    UPDATING = 4
    DELETING = 5

class VPC:
    def __init__(self, name, region, subnets = None, routerVM = None, status = VPCStatus.UNDEFINED.name, _id = None):
        self._id = _id
        self.name = name
        self.region = region
        self.subnets: List[str] = subnets or []
        self.routerVM = routerVM
        self.status = VPCStatus[status]

    def add_subnet(self, db, subnet: Subnet):
        self.subnets.append(subnet.get_id())
        self.save(db)
    
    def remove_subnet(self, db, subnet: Subnet):
        self.subnets.remove(subnet.get_id())
        # TODO: delete subnet
        
        self.save(db)

    def list_subnets(self, db) -> List[Subnet]:
        return list(db.subnet.find({'_id': {'$in': self.subnets}}))
    
    def create_subnet(self, db, subnet:str, network_name, bridge_name):
        subnet: Subnet = Subnet(subnet, network_name, bridge_name)
        subnet.save(db)
        self.subnets.append(subnet.get_id())
        self.save(db)
        
        # add interface to router vm
        router_vm: VM = VM.find_by_id(db, self.routerVM)
        router_vm.connect_to_network(db, subnet.get_id())
        return subnet

    def remove_subnet(self, db, subnet:str):
        data = db.subnet.find({'subnet': subnet})
        if data:
            subnet = Subnet.from_dict(data)
            subnet.delete(db)
            self.subnets.remove(subnet.get_id())
            
            interfaces_datas = db.interface.find({'subnet_id': subnet.get_id()})
            if interfaces_datas:
                for interfaces_data in interfaces_datas:
                    connected_vm = VM.from_dict(db.vm.find({"_id": interfaces_data['instance_id']}))
                    connected_vm.disconnect_from_network(db, subnet.get_id())
    
    def create_router(self, db):
        name = 'sample_name'
        vCPU = 1
        vMem = 2
        disk_size = 10
        router_vm = VM(name, vCPU, vMem, disk_size)
        router_vm.save(db)
        sb = Subnet.find_by_name(db, 'infra')
        router_vm.connect_to_network(db, sb.get_id(), default= True)
        self.routerVM = router_vm.get_id()
        self.save(db)

    def get_router(self) -> VM:
        return VM.find_by_id(self.routerVM)
    

    def has_router(self, db):
        return self.routerVM is not None

    def update_router(self, db):
        # TODO update router vm etc
        pass

    def update_router_status(self, db):
        # TODO update status of router - defined, running, suspended, shutdown, undefined
        pass

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
        return {"name": self.name, "region": self.region, "subnets": self.subnets, 'routerVM': self.routerVM, "status": self.status.name}
    
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
        return VPC(data['name'], data['region'], data['subnets'], data['routerVM'], status=data['status'], _id = data['_id'], )

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
