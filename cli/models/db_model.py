from pymongo import MongoClient
class DB:
    def __init__(self):
        self.uri  = 'mongodb://localhost:27017/'
        self.connected = False
        self.error = False
        self.client = None

    def connect(self):
        if not self.uri and not self.error:
            raise Exception("URI is empty")
        self.client =  MongoClient(self.uri)
        self.connected = self.isConnected()
    
    def isConnected(self):
        try:
            self.client.admin.command('ping')
            print("Successfully connected to db")
            return True
        except Exception:
            self.connected = False
            self.error = True
            raise
    
    def get_client(self):
        if self.connected and not self.error and self.client:
            return self.client
        else:
            self.connect()
            return self.get_client()