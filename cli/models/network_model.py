# #network
# {
#     'name': 'br1',
# }


from utils import Utils

class Network:
    def __init__(self, name, type = 'l2', default = False, nat = False, dhcp = False, _id = None):
        self._id = _id
        self.type = 'l2'
        self.name = name
        self.nat = False
        self.dhcp = False

    def save(self, db):
        if self._id is None:
            obj = db.network.insert_one(self.to_dict())
            inserted_id = obj.inserted_id
            self._id = inserted_id
        else:
            db.network.update_one({'_id': self._id}, {'$set': self.to_dict()})
    
    def get_id(self):
        return self._id

    def to_dict(self):
        return {"name": self.name, "vpcs": self.vpcs}
    
    def delete(self, db):
        if self._id is not None:
            db.network.delete_one({'_id': self._id})
            self._id = None

    def json(self):
        Utils.print_json(self.to_dict())

    @staticmethod
    def from_dict(data):
        return Network(data['name'], data['subnet_range'], data['subnet_mask'], _id = data['_id'])

    @staticmethod
    def find_by_name(db, name):
        data = db.network.find_one({'name':name})
        if data:
            return Network.from_dict(data)
        return None
    
    @staticmethod
    def find_by_id(db, id):
        data = db.network.find_one({'_id': Utils.id(id)})
        if data:
            return Network.from_dict(data)
        return None
