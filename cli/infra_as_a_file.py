import yaml
import traceback

from constants.infra_constants import HOST_PUBLIC_NETWORK
from utils.ip_utils import IPUtils
from controllers.tenant_controller import TenantController
from controllers.vpc_controller import VPCController
from controllers.container_controller import ContainerController

from models.tenant_model import Tenant
from models.vpc_model import VPC
from models.subnet_model import Subnet
from models.container_model import Container
from models.interface_model import Interface
from models.lb_model import LBType, LoadBalancer

from models.db_model import DB


def dbclient():
    db = DB()
    try:
        client = db.get_client()
    except Exception:
        traceback.print_exc()
        exit(1)
    db = client['ln']
    return db
db = dbclient()

def create_infra(file_name):
    print_rows = []
    with open(file_name, 'r') as file:
        data = yaml.safe_load(file)
        
    for tenant_name, infra_data in data.items():
        _tenant = Tenant.find_by_name(db, tenant_name)
        if _tenant is None:
            _tenant = Tenant(tenant_name).save(db)
        for vpc_name, vpc_data in infra_data.items():
            _vpc = None
            for _ in _tenant.vpcs:
                __vpc = VPC.find_by_id(db, _)
                if __vpc.name == vpc_name:
                    _vpc = __vpc
                    break
            if _vpc is None:
                _vpc = TenantController.create_vpc(db, _tenant, vpc_name)
            
            lb_app_name = vpc_data['lb']['name']
            lb_type = vpc_data['lb']['type']
            
            print(lb_app_name)
            if lb_type not in [LBType.IAAS.name, LBType.VM.name]:
                print("Invalid LB type")
                exit(1)
            
            subnets = []
            _lb_ips = []
            for sb_data in vpc_data['subnets']:
                sb_name = sb_data['name']
                sb_cidr = sb_data['cidr']
                subnets.append({"name": sb_name, "cidr": sb_cidr})
                _subnet = Subnet.find_by_name(db, f"{tenant_name}{vpc_name}{sb_name}")
                if _subnet is None:
                    _subnet = VPCController.create_subnet_in_container(db, _vpc.get_id(), sb_name, sb_cidr)
                
                print_rows.append("Containers data")
                for _container_data in sb_data['servers']:
                    print(_container_data)
                    name = _container_data['name']
                    image = _container_data['image']
                    vcpu = _container_data['vcpu']
                    mem = _container_data['mem']
                    region = _container_data['region']
                    weight = _container_data['weight']
                    
                    _cont = Container.find_by_name(db, name)
                    if _cont is None:
                        _cont = Container(name, image, region, vcpu, mem).save(db)
                        default_route = IPUtils.get_default_subnet_gateway(db, _subnet.get_id(), _cont.region)
                        ContainerController.create(db, _cont.get_id())
                        ContainerController.connect_to_network(db, _cont.get_id(), _subnet.get_id(), default_route)
                        _cont = Container.find_by_id(db, _cont.get_id())
                        _cont_ip = Interface.find_by_id(db, _cont.interfaces[0]).ip_address
                        _lb_ips.append({"ip_address": _cont_ip, "weight": weight})
                        print_rows.append(f"{name} - {_cont_ip}")
            
            _vpc = VPC.find_by_id(db, _vpc.get_id())
            if not _vpc.lbs:
                pub_sb = Subnet.find_by_name(db, HOST_PUBLIC_NETWORK)
                lb_ip = IPUtils.get_unique_ip_from_region(db, pub_sb.get_id(), 'east')
                ContainerController.create_load_balancer(db, _tenant.get_id(), _vpc.get_id(), lb_app_name, lb_ip, LBType[lb_type])
            
            print_rows.append("\nLoad name - Public IP")
            
            lb = LoadBalancer.find_by_id(db, _vpc.lbs[lb_app_name])
            
            _vpc = VPC.find_by_id(db, _vpc.get_id())
            ContainerController.add_ip_targets(db,  _tenant.get_id(), _vpc.get_id(), lb_app_name, _lb_ips)
            
            print_rows.append(f"{lb.name} - {lb.lb_ip}")
            
    for row in print_rows:
        print(row)

if __name__ == "__main__":
    create_infra('infra/sample.yml')