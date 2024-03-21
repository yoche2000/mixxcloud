from pymongo import MongoClient


def main():

    connection_string = 'mongodb://localhost:27017/'

    client = MongoClient(connection_string)
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
    db = client['ln']
    collection = db['lb']

    document = {"name": "John Doe", "age": 30}
    result = collection.insert_one(document)

    print(f"Inserted document with id: {result.inserted_id}")


if __name__ == '__main__':
    main()