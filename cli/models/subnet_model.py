# #vpc
# {
#     'region': "us-east1",
#     'subnets': [subnet_id]
#     '_subnets': Subnet()
# }


from enum import Enum
from utils.utils import Utils
from ipaddress import ip_network, IPv4Network
from bson.objectid import ObjectId
from controllers.subnet_controller import SubnetController

class SubnetStatus(Enum):
    UNDEFINED = 1
    STARTING = 2
    RUNNING = 3
    UPDATING = 4
    DELETING = 5
    ERROR = 6
    
class SubnetType(Enum):
    DEFAULT = 1
    NAT = 2
    


class Subnet:
    def __init__( self,
                  subnet,
                  network_name,
                  bridge_name,
                  status = SubnetStatus.UNDEFINED.name,
                  type = SubnetType.DEFAULT.name,
                  _id = None ):
        
        self._id = _id
        self.network_name = network_name #libvirt
        self.bridge_name = bridge_name #brctl
        
        # 192.168.2.0/24
        # 192.168.2.1 - GATEWAY
        # 192.168.2.2 - IP START
        # 192.168.2.255 - IP RANGE
        self.subnet = subnet #192.168.2.0/24
        self._subnet: IPv4Network = ip_network(subnet)
        self.status = SubnetStatus[status]
        # TODO: Add these fields
        # self.ip_adress = 192.168.2.1 - GATEWAY
        # self.mask = 255.255.255.0 - netmask
        self.type = SubnetType[type]
    
    # @staticmethod
    # def create_subnet(db, subnet, network_name, bridge_name):
    def define_net(self, db):
        self.status = SubnetStatus.STARTING
        self.save(db)
        def success():
            self.status = SubnetStatus.RUNNING
            self.save(db)
        def failure():
            self.status = SubnetStatus.ERROR
            self.save(db)
        try:
            SubnetController.createBridge(self.bridge_name, success=success, failure=failure)
        except:
            failure()
    
    def undefine_net(self, db):
        self.status = SubnetStatus.DELETING
        self.save(db)
        def success():
            self.status = SubnetStatus.UNDEFINED
            self.save(db)
        def failure():
            self.status = SubnetStatus.ERROR
            self.save(db)
        try:
            SubnetController.rmBridge(self.bridge_name, success=success, failure=failure)
        except:
            failure()

    def _define_libvirt_net(self):
        pass
    
    def _define_brctl_net(self):
        pass


    def _undefine_libvirt_net(self):
        pass
    
    def _undefine_brctl_net(self):
        pass
    
    def status(self):
        # TODO: Perform checks on the system
        return self.status.name

    def is_private(self):
        return self._subnet.is_private
    
    def get_host_mask(self):
        return self.subnet.split('/')[1]

    def get_ipobj(self):
        return self._subnet

    def save(self, db):
        if self._id is None:
            obj = db.subnet.insert_one(self.to_dict())
            inserted_id = obj.inserted_id
            self._id = inserted_id
        else:
            db.subnet.update_one({'_id': self._id}, {'$set': self.to_dict()})
        return self
    
    def get_id(self):
        return self._id

    def to_dict(self):
        return {"subnet": self.subnet,
                "network_name": self.network_name,
                "bridge_name": self.bridge_name,
                "type": self.type.name,
                "status": self.status.name
                }
    
    def delete(self, db):
        if self._id is not None:
            db.subnet.delete_one({'_id': self._id})
            self._id = None

    def json(self):
        Utils.print_json(self.to_dict())

    @staticmethod
    def from_dict(data):
        return Subnet(data['subnet'],
                      data['network_name'],
                      data['bridge_name'],
                      status=data['status'],
                      type=data['type'],
                      _id = data['_id'])

    @staticmethod
    def find_by_name(db, network_name):
        data = db.subnet.find_one({'network_name':network_name})
        if data:
            return Subnet.from_dict(data)
        return None
    
    @staticmethod
    def find_by_id(db, id: str | ObjectId):
        if isinstance(id, str):
            id = ObjectId(id)
        data = db.subnet.find_one({'_id': id})
        if data:
            return Subnet.from_dict(data)
        return None
