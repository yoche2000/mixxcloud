from pymongo import MongoClient
import pprint

def main():

    connection_string = 'mongodb://localhost:27017/'

    client = MongoClient(connection_string)
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db_list = client.list_database_names()
    print("Databases available:")
    for db_name in db_list:
        print(db_name)

    db = client['ln']
    collection_list = db.list_collection_names()
    print(f"Collections available in the database ln:")
    for collection_name in collection_list:
        print(collection_name)

    print('---')
    collection = db['ln']
    document = {
        "name": "John Doe",
        "age": 40,
        "email": "johndoe@example.com"
    }
    result = collection.insert_one(document)
    print(f"Inserted document with ID: {result.inserted_id}")
    documents = collection.find({})
    # print(len(documents))
    for doc in documents:
        pprint.pprint(doc)



if __name__ == '__main__':
    main()