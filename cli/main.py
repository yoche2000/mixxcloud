from models import DB, Tenant
from utils import Utils
import traceback

import pprint

def main():
    db1 = DB()
    try:
        client = db1.get_client()
    except Exception:
        traceback.print_exc()
        exit(1)

    db_list = client.list_database_names()
    print("Databases available:")
    for db_name in db_list:
        print(db_name)

    db = client['ln']
    collection_list = db.list_collection_names()
    print(f"Collections available in the database ln:")
    for collection_name in collection_list:
        print(collection_name)

    tent = Tenant("VPC5")
    tent.save(db)

    documents = db.tenant.find({})

    for doc in documents:
        tmp = Tenant.from_dict(doc)
        tmp.json()


if __name__ == '__main__':
    main()