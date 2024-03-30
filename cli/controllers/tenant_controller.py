from typing import List
from controllers.vpc_controller import VPCController
from models.tenant_model import Tenant
from bson.objectid import ObjectId
from models.vpc_model import VPC

class TenantController:
    # use
    # db, tenant_name, vpc_name, region
    @staticmethod
    def create_vpc(db, tenant: Tenant | str, name: str, region: str):
        if isinstance(tenant, str):
            tenant = Tenant.find_by_name(db, tenant)
        vpcs = [ VPC.find_by_id(db, i) for i in tenant.vpcs]
        print("Checking for any Conflicting VPCs..")
        found = False
        for vpc in vpcs:
            if vpc.name == name:
                found = True
                print("Cannot create vpc of same name..")
                return False
        if not found:
            vpc = VPC(name, region)
            vpc.save(db)
            print("No Conflicting VPCs found, saving the configuration..")
            VPCController.create_router(db, tenant, vpc)
            tenant.vpcs.append(vpc.get_id())
            tenant.save(db)
        return True
    
    
    @staticmethod
    def add_vpc(db, tenant: Tenant | str , vpc_id: ObjectId | str):
        if isinstance(tenant, str):
            tenant = Tenant.find_by_name(db, tenant)
        if isinstance(vpc_id, str):
            vpc_id = ObjectId(vpc_id)
        if vpc_id not in tenant.vpcs:
            tenant.vpcs.append(vpc_id)
        tenant.save(db)
    
    # use
    # db, tenant_name, vpc_id (of the vpc you want to delete)
    @staticmethod
    def delete_vpc(db, tenant: Tenant | str, vpc_id: ObjectId | str):
        if isinstance(tenant, str):
            tenant = Tenant.find_by_name(db, tenant)
        if isinstance(vpc_id, str):
            vpc_id = ObjectId(vpc_id)
        if vpc_id in tenant.vpcs:
            tenant.vpcs.remove(vpc_id)
        tenant.save(db)
    
    @staticmethod
    def list_vpcs(db, tenant: Tenant | str) -> List[VPC]:
        if isinstance(tenant, str):
            tenant = Tenant.find_by_name(db, tenant)
        return [VPC.from_dict(data) for data in  list(db.vpc.find({'_id': {'$in': tenant.vpcs}}))]

    @staticmethod
    def get_vpc_by_tenant_vpc_name(db, tenant: Tenant | str, vpc_name: str ) -> Tenant | None:
        if isinstance(tenant, str):
            tenant = Tenant.find_by_name(db, tenant)
        if isinstance(vpc_name, str):
            for vpc_id in tenant.vpcs:
                tmp: VPC = VPC.find_by_id(db, vpc_id)
                if tmp.name == vpc_name:
                  return tmp