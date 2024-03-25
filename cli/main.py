# from models.vm_model import VM
# from models import  Tenant, VM
from models.db_model import DB
from models.vm_model import VM
from models.interface_model import Interface
# from models.vpc_model import VPC
import traceback
from utils.utils import Utils

def main():
    db1 = DB()
    try:
        client = db1.get_client()
    except Exception:
        traceback.print_exc()
        exit(1)
    db = client['ln']
    
    # vm = VM.find_by_name(db, 'VM1')
    # name, vCPU, vMem, disk_size
    # vm = VM('VM1', 1, 2, 10)
    vm = VM.find_by_name(db, 'VM1')
    # # db, ip_address, mac_address, network_mask, gateway
    vm.add_interface(db, '192', 'mac_add', 'mask', 'gateway')
    vm.add_interface(db, '168', 'mac_add', 'mask', 'gateway')
    list_1 = vm.list_interfaces(db)
    print(list_1)
    vm.remove_interface(db, list_1[0].get_id())
    vm.save(db)
    # vm.json()
    # vm.save(db)
    

    # Utils.valid_ip_range('8.8.8.0','24')
    # Utils.valid_ip_range('192.168.2.0','30')
    # Utils.valid_ip_range('192.168.3.0','30')

    # db_list = client.list_database_names()
    # print("Databases available:")
    # for db_name in db_list:
    #     print(db_name)

    # db = client['ln']
    # collection_list = db.list_collection_names()
    # print(f"Collections available in the database ln:")
    # for collection_name in collection_list:
    #     print(collection_name)

    # # tent = Tenant("VPC5")
    # # tent.save(db)

    # # documents = db.tenant.find({"_id": Utils.id('65fcfa155490d356cd5d626f')})
    
    # x = Tenant.find_by_id(db, "65fcfa155490d356cd5d626f")
    # x.json()
    # x.name = "test"
    # x.save(db)


    # for doc in documents:
    #     print("Hello")
    #     tmp = Tenant.from_dict(doc)
    #     print(tmp._id)
    #     tmp.name = "new_name"
    #     tmp.save()



if __name__ == '__main__':
    main()