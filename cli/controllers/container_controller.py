from ipaddress import IPv4Address, ip_network
from bson.objectid import ObjectId
from Container_automation.workflows import Container_CRUD_Workflows
from models.vpc_model import VPC
from models.interface_model import Interface
from models.container_model import Container
from models.subnet_model import Subnet
from constants.infra_constants import REGION_MAPPING
import random
from utils.ip_utils import IPUtils
from ipaddress import ip_network

class ContainerController():
    @staticmethod
    def create(db, c_id: ObjectId):
        cont = Container.find_by_id(db,c_id)
        container_name = cont.name
        container_image = cont.image
        region = cont.region
        Container_CRUD_Workflows.run_ansible_playbook_for_container_creation(container_name, container_image, REGION_MAPPING[region])
        
    
    @staticmethod
    def up():
        pass
    
    @staticmethod
    def down():
        pass
    
    @staticmethod
    def delete():
        pass
    
    @staticmethod
    def connect_to_network(db, c_id: ObjectId, sb_id: ObjectId, default_route = None, is_nat = False):
        container = Container.find_by_id(db, c_id)
        subnet = Subnet.find_by_id(db, sb_id)
        region = container.region
        
        ip_address = IPUtils.get_unique_ip_from_region(db, sb_id, region) 
        
        container_name = container.name
        bridge_name = subnet.bridge_name
        
        net_interface = Interface(ip_address, None, None, default_route, c_id, sb_id, None, is_nat=is_nat)
        net_interface.save(db)
        
        container.interfaces.append(net_interface.get_id())
        container.save(db)
        
        ip_address = ip_address + '/' + subnet.get_host_mask()
        print(container_name, bridge_name, ip_address, default_route, REGION_MAPPING[region])
        
        
        Container_CRUD_Workflows.run_ansible_playbook_for_container_to_sb_connection(container_name, bridge_name, ip_address, default_route, REGION_MAPPING[region], is_nat)
        
        
    @staticmethod
    def create_subnet_in_container(db, vpc_id: ObjectId, subnet_name: str, cidr: str, ):
        vpc = VPC.find_by_id(db, vpc_id)
        cont_even = Container.find_by_id(db, vpc.container_west)
        cont_odd = Container.find_by_id(db, vpc.container_east)
        
        _inf_even = Interface.find_by_id(db, cont_even.interfaces[0])
        _inf_odd = Interface.find_by_id(db, cont_odd.interfaces[0])
        
        # dft_sb = Subnet.find(db, _inf_0.subnet_id)
        
        container_name = cont_even.name
        # subnet = cidr
        # gateway_even_ip = 
        
        # container_name: KVPC
        # subnet_name: KS1
        # subnet: 10.2.2.0/24
        # gateway: 10.2.2.1/24
        # vni_id: 10
        # local_ip: 172.16.1.7
        # remote_ip: 172.16.1.6
        
        
        nw_obj = ip_network(cidr)
        
        pipeline = [
            {"$group": {"_id": None, "maxValue": {"$max": "$vni_id"} }}
        ]
        sb_max_vni = list(db['subnet'].aggregate(pipeline))[0]['maxValue']
        if sb_max_vni < 10:
            sb_max_vni = 9
            
        vni_id = sb_max_vni + 1
        print(cont_even.name+subnet_name)
        sb = Subnet(cidr, cont_even.name+subnet_name, cont_even.name+subnet_name, vni_id).save(db)
        # sb = Subnet(cidr, subnet_name, subnet_name, vni_id)
        vpc.subnets.append(sb.get_id())
        vpc.save(db)
        
        Container_CRUD_Workflows.run_ansible_playbook_for_container_subnet_creation(
            container_name,
            subnet_name,
            cidr,
            f"{str(nw_obj[2])}/{cidr.split('/')[1]}",
            vni_id,
            _inf_even.ip_address,
            _inf_odd.ip_address,
            region = REGION_MAPPING[cont_even.region],
            )
        Container_CRUD_Workflows.run_ansible_playbook_for_container_subnet_creation(
            container_name,
            subnet_name,
            cidr,
            f"{str(nw_obj[1])}/{cidr.split('/')[1]}",
            vni_id,
            _inf_odd.ip_address,
            _inf_even.ip_address,
            region = REGION_MAPPING[cont_odd.region]
            )
        return sb
    
    