from typing import List
from controllers.vpc_controller import VPCController
from models.tenant_model import Tenant
from bson.objectid import ObjectId
from models.vpc_model import VPC, VPCStatus
from controllers.container_controller import ContainerController

class TenantController:
    # use
    # db, tenant_name, vpc_name, region
    @staticmethod
    def create_vpc(db, tenant: Tenant | str, name: str) -> VPC | None:
        if isinstance(tenant, str):
            tenant = Tenant.find_by_name(db, tenant)
        vpcs = [ VPC.find_by_id(db, i) for i in tenant.vpcs]
        print("Checking for any Conflicting VPCs..")
        found = False
        for vpc in vpcs:
            if vpc.name == name:
                found = True
                print("Cannot create vpc of same name..")
                return None
        if not found:
            vpc = VPC(name)
            vpc.save(db)
            print("No Conflicting VPCs found, saving the configuration..")
            VPCController.create_router(db, tenant, vpc)
            tenant.vpcs.append(vpc.get_id())
            tenant.save(db)
        return vpc
    
    @staticmethod
    def delete_vpc(db, tenant: Tenant | str, vpc_id: str):
        if isinstance(tenant, str):
            tenant = Tenant.find_by_name(db, tenant)
        _vpc = VPC.find_by_id(db, vpc_id)
        try: 
            _vpc.status = VPCStatus.DELETING
            _vpc.save(db)
            
            if _vpc is not None:
                ContainerController.delete_container(db, vpc_id, _vpc.container_east)
                ContainerController.delete_container(db, vpc_id, _vpc.container_west)
                
            _vpc = VPC.find_by_id(db, vpc_id)
            _vpc.status = VPCStatus.UNDEFINED
            _vpc.save(db)
        except:
            _vpc = VPC.find_by_id(db, vpc_id)
            _vpc.status = VPCStatus.ERROR
            _vpc.save(db)
            
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