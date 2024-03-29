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


class VPCStatus(Enum):
    UNDEFINED = 1
    CREATING = 2
    RUNNING = 3
    UPDATING = 4
    DELETING = 5
    ERROR = 6

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
        router_vm.connect_to_network(db, subnet.get_id(), is_gateway=True, load_balancing_interface=False)
        return subnet

    def up(self, db):
        if self.status == VPCStatus.RUNNING:
            return True
        elif self.status == VPCStatus.ERROR:
            self.down(db)
        self.status = VPCStatus.CREATING
        self.save(db)
        try:
            if self.routerVM is None:
                self.create_router(db)
                for subnet_id in self.subnets:
                    sb = Subnet.find_by_id(subnet_id)
                router_vm: VM = VM.find_by_id(db, self.routerVM)
                router_vm.connect_to_network(db, sb.get_id(), is_gateway=True, load_balancing_interface=False)
            
            for subnet_id in self.subnets:
                sb = Subnet.find_by_id(subnet_id)
                sb.define_net(db)
            
            vm = VM.find_by_id(self.routerVM)
            vm.start(db)
        
        except:
            self.status = VPCStatus.ERROR
            self.save(db)


    def down(self, db):
        if self.status == VPCStatus.UNDEFINED:
            return True
        try:
            router_vm = VM.find_by_id(self.routerVM)
            router_vm.undefine(db)
            
            for subnet_id in self.subnets:
                sb = Subnet.find_by_id(subnet_id)
                sb.undefine_net(db)
            
        except:
            self.status = VPCStatus.ERROR
            self.save(db)

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


    def get_router(self) -> VM:
        return VM.find_by_id(self.routerVM)

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
        print(data)
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
