from enum import Enum
from typing import List
from .interface_model import Interface
from utils.utils import Utils

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


    def list_interfaces(self, db):
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
