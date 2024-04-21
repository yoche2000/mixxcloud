from ipaddress import IPv4Address, ip_network
from typing import List
from bson.objectid import ObjectId
from Container_automation.workflows import Container_CRUD_Workflows, LB_CRUD_Workflows, Subnet_CRUD_Workflows
from models.lb_model import LBType, LoadBalancer
from models.vpc_model import VPC, VPCStatus
from models.interface_model import Interface
from models.container_model import Container, ContainerStatus
from models.subnet_model import Subnet
from constants.infra_constants import REGION_MAPPING
from utils.ip_utils import IPUtils
from ipaddress import ip_network
from constants.infra_constants import HOST_PUBLIC_NETWORK
import traceback

class ContainerController():
    @staticmethod
    def create(db, c_id: ObjectId):
        try:
            cont = Container.find_by_id(db,c_id)
            if cont.status == ContainerStatus.RUNNING or cont.status == ContainerStatus.UPDATING:
                return True
            cont.status = ContainerStatus.UPDATING
            cont.save(db)
            
            container_name = cont.name
            container_image = cont.image
            region = cont.region
            vcpu = cont.vCPU
            mem = cont.mem
            Container_CRUD_Workflows.run_ansible_playbook_for_container_creation(container_name, container_image, REGION_MAPPING[region], vcpu=vcpu, mem=mem)
            cont.status = ContainerStatus.RUNNING
            cont.save(db)
            return True
        except:
            cont.status = ContainerStatus.ERROR
            cont.save(db)
            return False
    
    @staticmethod
    def connect_to_network(db, c_id: ObjectId, sb_id: ObjectId, default_route = None, is_nat = False, ip_address: str = None, no_ip = False):
        try:
            container = Container.find_by_id(db, c_id)
            subnet = Subnet.find_by_id(db, sb_id)
            if container.status == ContainerStatus.ERROR or container.status == ContainerStatus.UPDATING:
                return True
            container.status = ContainerStatus.UPDATING
            container.save(db)
            if ip_address is None:
                ip_address = IPUtils.get_unique_ip_from_region(db, sb_id, container.region) 
            
            container_name = container.name
            bridge_name = subnet.bridge_name
            
            net_interface = Interface(ip_address, None, None, default_route, c_id, sb_id, None, is_nat=is_nat)
            if not no_ip:
                net_interface.save(db)
            
            container.interfaces.append(net_interface.get_id())
            container.save(db)
            
            if ip_address:
                ip_address = ip_address + '/' + subnet.get_host_mask()
            # print(container_name, bridge_name, ip_address, default_route, REGION_MAPPING[region])
            if no_ip:
                ip_address = None
    
            Container_CRUD_Workflows.run_ansible_playbook_for_container_to_sb_connection(container_name, bridge_name, ip_address, default_route, REGION_MAPPING[container.region], is_nat)
            container.status = ContainerStatus.RUNNING
            container.save(db)
            return True
        except:
            traceback.print_exc()
            container.status = ContainerStatus.ERROR
            container.save(db)
            return False        
        
    @staticmethod
    def delete_container(db, vpc_id: ObjectId, c_id: ObjectId):
        try:
            cont = Container.find_by_id(db, c_id)
            if cont.status == ContainerStatus.UPDATING:
                return False
            cont.status = ContainerStatus.DELETING
            cont.save(db)
            Container_CRUD_Workflows.run_ansible_playbook_for_container_deletion(cont.name, REGION_MAPPING[cont.region])
            
            cont = Container.find_by_id(db, c_id)
            cont.status = ContainerStatus.UNDEFINED
            cont.save(db)
            return True
        except:
            traceback.print_exc()
            cont = Container.find_by_id(db, c_id)
            cont.status = ContainerStatus.ERROR
            cont.save(db)
            return False
    
    @staticmethod
    def create_load_balancer(db, tenant_id: ObjectId, vpc_id: ObjectId, lb_name: str, lb_ip: str, lb_type: LBType):
        try:
            vpc = VPC.find_by_id(db, vpc_id)

            if vpc.lbs:
                print("Load Balancer App already exists")
                return True
            
            if vpc.status == VPCStatus.UPDATING:
                return True

            vpc.status = VPCStatus.UPDATING
            vpc.save(db)
            
            if lb_type == LBType.IAAS:
                cont_east = Container.find_by_id(db, vpc.get_router('east'))
                cont_west = Container.find_by_id(db, vpc.get_router('west'))
            
            elif lb_type == LBType.VM:
                cont_east = Container(f'LB{vpc.name}', 'vpcrouter', 'east', 1, 1024).save(db)
                cont_west = Container(f'LB{vpc.name}', 'vpcrouter', 'west', 1, 1024).save(db)
                
                ContainerController.create(db, cont_east.get_id())
                ContainerController.create(db, cont_west.get_id())
                
                # LB Container should have have default route
                # flag = True
                # LB Container should have not have default route
                flag = False
                
                for sb_id in vpc.subnets:
                    ContainerController.connect_to_network(db, 
                                                            cont_east.get_id(),
                                                            sb_id,
                                                            IPUtils.get_default_subnet_gateway(db, sb_id, cont_east.region) if flag else None,
                                                            False)
                    ContainerController.connect_to_network(db,
                                                            cont_west.get_id(),
                                                            sb_id,
                                                            IPUtils.get_default_subnet_gateway(db, sb_id, cont_west.region) if flag else None,
                                                            False)
                    flag = False

            lb = LoadBalancer(lb_name,
                              vpc_id,
                              type = lb_type.name,
                              instance_east = cont_east.get_id(),
                              instance_west = cont_west.get_id(),
                              target_group = [],
                              lb_ip = lb_ip,
                              )
            lb.save(db)
            
            pub_sb = Subnet.find_by_name(db, HOST_PUBLIC_NETWORK)
            
            ContainerController.connect_to_network(db, cont_east.get_id(), pub_sb.get_id(), None, False, ip_address= lb_ip)
            ContainerController.connect_to_network(db, cont_west.get_id(), pub_sb.get_id(), None, False, no_ip= True)
            
            if not vpc.lbs:
                vpc.lbs = {}
            vpc.lbs[lb_name] = lb.get_id()
            vpc.save(db)
            
            vpc = VPC.find_by_id(db, vpc_id)
            vpc.status = VPCStatus.RUNNING
            vpc.save(db)
            
            return True
        except:
            vpc = VPC.find_by_id(db, vpc_id)
            vpc.status = VPCStatus.ERROR
            vpc.save(db)
            traceback.print_exc()
            return False
        
    @staticmethod
    def delete_loadbalancer(db, tenant_id: ObjectId, vpc_id: ObjectId, lb_name: str):
        try:
            vpc = VPC.find_by_id(db, vpc_id)
            if not vpc.lbs:
                print("Load Balancer doesn't exist")
                return True
            
            if vpc.status == VPCStatus.UPDATING:
                return True

            vpc.status = VPCStatus.UPDATING
            vpc.save(db)
            
            lb = LoadBalancer.find_by_id(db, vpc.lbs[lb_name])
            if lb.type == LBType.IAAS:
                ContainerController.delete_ip_rules(db, tenant_id, vpc_id, lb_name)
            elif lb.type == LBType.VM:
                ContainerController.delete_ip_rules(db, tenant_id, vpc_id, lb_name)
                ContainerController.delete_container(db, vpc_id, lb.instance_east)
                ContainerController.delete_container(db, vpc_id, lb.instance_west)
            lb.delete(db)
            vpc.lbs = {}
            vpc.save(db)
            vpc = VPC.find_by_id(db, vpc_id)
            vpc.status = VPCStatus.RUNNING
            vpc.save(db)
        except:
            vpc = VPC.find_by_id(db, vpc_id)
            vpc.status = VPCStatus.ERROR
            vpc.save(db)
            traceback.print_exc()
            return False
    
    @staticmethod
    def add_ip_targets(db, tenant_id: ObjectId, vpc_id: ObjectId, lb_name: str, ip_addresses):
        try:
            vpc = VPC.find_by_id(db, vpc_id)
            lb = LoadBalancer.find_by_id(db, vpc.lbs[lb_name])
            
            for ip_add in ip_addresses:
                ip = ip_add['ip_address']
                weight = ip_add['weight']
                lb.add_ip_address(db, ip, weight)
            
            ContainerController.create_lb_rules(db, tenant_id, vpc_id, lb_name)
        except:
            traceback.print_exc()
            return False
        
    @staticmethod
    def remove_ip_tartgets(db, tenant_id: ObjectId, vpc_id: ObjectId, lb_name: str, ip_addresses: List[str],):
        try:
            vpc = VPC.find_by_id(db, vpc_id)
            lb = LoadBalancer.find_by_id(db, vpc.lbs[lb_name])
            
            for ip_add in ip_addresses:
                lb.rm_ip_address(db, ip_add)
            
            ContainerController.delete_ip_rules(db, tenant_id, vpc_id, lb_name)
        except:
            traceback.print_exc()
            return False
        
    @staticmethod
    def create_lb_rules(db, tenant_id: ObjectId, vpc_id: ObjectId, lb_name: str):
        try:
            vpc = VPC.find_by_id(db, vpc_id)
            lb = LoadBalancer.find_by_id(db, vpc.lbs[lb_name])
            
            if not lb:
                return False
            
            if vpc.status == VPCStatus.UPDATING:
                return True
            
            vpc.status = VPCStatus.UPDATING
            vpc.save(db)
            
            if vpc.lb_running:
                ContainerController.delete_ip_rules(db, tenant_id, vpc_id, lb_name)
            
            instance_east = Container.find_by_id(db, lb.instance_east)
            instance_west = Container.find_by_id(db, lb.instance_west)
            
            cal_ip_weights = weight_to_prob(lb.target_group)
            out_tenant_ips = {}
            for i in range(len(cal_ip_weights)):
                for ip, weight in cal_ip_weights[i].items():
                    out_tenant_ips[ip] = weight
            
            if lb.type == LBType.IAAS:
                snat_east = IPUtils.get_default_subnet_gateway(db, vpc.subnets[0], instance_east.region)
                snat_west = IPUtils.get_default_subnet_gateway(db, vpc.subnets[0], instance_west.region)
            else:
                _0_int_east = Interface.find_by_id(db, instance_east.interfaces[0])
                snat_east = _0_int_east.ip_address
                
                _0_int_west = Interface.find_by_id(db, instance_west.interfaces[0])
                snat_west = _0_int_west.ip_address
            
            LB_CRUD_Workflows.run_ansible_playbook_for_lb_rules(instance_east.name, lb.lb_ip, snat_east, out_tenant_ips, REGION_MAPPING[instance_east.region])
            LB_CRUD_Workflows.run_ansible_playbook_for_lb_rules(instance_west.name, lb.lb_ip, snat_west, out_tenant_ips, REGION_MAPPING[instance_west.region])
            vpc.lb_running = True
            vpc.save(db)
            
            vpc = VPC.find_by_id(db, vpc_id)
            vpc.status = VPCStatus.RUNNING
            vpc.save(db)
            return True
        except:
            vpc = VPC.find_by_id(db, vpc_id)
            vpc.status = VPCStatus.ERROR
            vpc.save(db)
            traceback.print_exc()
            return False
    
    @staticmethod
    def delete_ip_rules(db, tenant_id: ObjectId, vpc_id: ObjectId, lb_name: str):
        try:
            vpc = VPC.find_by_id(db, vpc_id)
            lb = LoadBalancer.find_by_id(db, vpc.lbs[lb_name])
            
            if vpc.status == VPCStatus.UPDATING:
                return False
            
            vpc.status == VPCStatus.UPDATING
            vpc.save(db)
            
            instance_east = Container.find_by_id(db, lb.instance_east)
            instance_west = Container.find_by_id(db, lb.instance_west)
            
            LB_CRUD_Workflows.run_ansible_playbook_for_lb_rules_deletion(instance_east.name, lb.type == LBType.IAAS, region=instance_east.region)
            LB_CRUD_Workflows.run_ansible_playbook_for_lb_rules_deletion(instance_west.name, lb.type == LBType.IAAS, region=instance_west.region)
            vpc.lb_running = False
            vpc.save(db)
            
            vpc = VPC.find_by_id(db, vpc_id)
            vpc.status = VPCStatus.RUNNING
            vpc.save(db)
        except:
            vpc = VPC.find_by_id(db, vpc_id)
            vpc.status = VPCStatus.ERROR
            vpc.save(db)
            return False


def weight_to_prob(ip_weight_list):
    def sum_of_weights():
        tmp = 0
        for i in range(len(ip_weight_list)):
            tmp += ip_weight_list[i]['weight']
        return tmp
        
    # print(ip_weight_list)
    result = []
    for i in range(len(ip_weight_list)):
        perc =  ip_weight_list[i]['weight'] / sum_of_weights()
        ip_weight_list[i]['weight'] = 0
        result.append({ip_weight_list[i]['ip']:perc})
    return(result)