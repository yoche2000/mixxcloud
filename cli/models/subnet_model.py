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
# from controllers.subnet_controller import SubnetController
# from utils.ip_utils import IPUtils
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
                 cidr,
                 network_name,
                 bridge_name,
                 vni_id,
                 vpc_id,
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
        self.cidr = cidr #192.168.2.0/24
        self._subnet: IPv4Network = ip_network(cidr)
        self.status = SubnetStatus[status]
        self.subnet_type = SubnetType[subnet_type]
        self.vni_id = vni_id
        self.vpc_id = vpc_id

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
        return self.cidr.split('/')[1]

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
        return {"cidr": self.cidr,
                "vni_id": self.vni_id,
                "network_name": self.network_name,
                "bridge_name": self.bridge_name,
                "type": self.subnet_type.name,
                "status": self.status.name,
                "vpc_id": self.vpc_id,
                }
    
    def delete(self, db):
        if self._id is not None:
            db.subnet.delete_one({'_id': self._id})
            self._id = None

    def json(self):
        Utils.print_json(self.to_dict())
        
    # def get_gateway(self, db, region: str):
    #     return IPUtils.get_unique_ip_from_region(db, self._id, region, is_gateway = True)

    @staticmethod
    def from_dict(data):
        return Subnet(data['cidr'],
                      data['network_name'],
                      data['bridge_name'],
                      data['vni_id'],
                      vpc_id=data['vpc_id'],
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
            #print(data)
            return Subnet.from_dict(data)
        return None
