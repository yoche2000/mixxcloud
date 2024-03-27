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
    def __init__(self,
                 subnet,
                 network_name,
                 bridge_name,
                 status = SubnetStatus.UNDEFINED.name,
                 subnet_type = SubnetType.DEFAULT.name,
                 _id = None,
                 ):
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
        self.subnet_type = SubnetType[subnet_type]
        print(subnet_type, self.subnet_type, self.network_name)
    
    # @staticmethod
    # def create_subnet(db, subnet, network_name, bridge_name):
    def define_net(self, db):
        if self.status == SubnetStatus.RUNNING:
            print("Subnet is already running")
            return True
        if self.status == SubnetStatus.STARTING or self.status == SubnetStatus.UPDATING:
            # don't update status since someother action is being performed on this object
            print("Cannot update at his time")
            return
        if self.status == SubnetStatus.ERROR:
            self.undefine_net(db)
        self.status = SubnetStatus.STARTING
        self.save(db)
        def success():
            self.status = SubnetStatus.RUNNING
            self.save(db)
        def failure():
            self.status = SubnetStatus.ERROR
            self.save(db)
        try:
            SubnetController.define(self.network_name, 
                                    self.bridge_name,
                                    cidr = self.subnet, 
                                    nat_enabled = SubnetType.NAT == self.subnet_type, 
                                    success=success, 
                                    failure=failure)
        except:
            return False
        return True
    
    def undefine_net(self, db):
        if self.status == SubnetStatus.UNDEFINED:
            return True
        if self.status == SubnetStatus.STARTING or self.status == SubnetStatus.UPDATING:
            # don't update status since someother action is being performed on this object
            print("Cannot update at his time")
            return 
        self.status = SubnetStatus.DELETING
        self.save(db)
        def success():
            self.status = SubnetStatus.UNDEFINED
            self.save(db)
        def failure():
            self.status = SubnetStatus.ERROR
            self.save(db)
        try:
            SubnetController.undefine(self.network_name,
                                      self.bridge_name,
                                      nat_enabled = SubnetType.NAT == self.subnet_type, 
                                      success=success,
                                      failure=failure)
        except:
            return False
        return True

    def get_gateway_ip(self):
        ip_addr = self._subnet.hosts()
        return str(next(ip_addr))

    def get_subnet_mask(self):
        return str(self._subnet.netmask)
    
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
                "type": self.subnet_type.name,
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
                      subnet_type=data['type'],
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
