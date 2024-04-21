from ipaddress import ip_network
import click
import shutil
import pyfiglet
from controllers.container_controller import ContainerController
from models.container_model import Container
from controllers.tenant_controller import TenantController
from controllers.subnet_controller import SubnetController
from controllers.vm_controller import VMController
from controllers.vpc_controller import VPCController
from controllers.vm_controller import VMController
from models.tenant_model import Tenant
from models.vpc_model import VPC
from models.vm_model import VM
from models.subnet_model import Subnet
from models.interface_model import Interface
from models.db_model import DB
from models.vpc_model import VPC
from models.lb_model import LoadBalancer, LBType
from models.vm_model import VM
import traceback
from bson.objectid import ObjectId
from utils.ip_utils import IPUtils
from constants.infra_constants import HOST_PUBLIC_NETWORK
# sudo apt-get install -y python3-pyfiglet
# Usage from main.py: sudo python3 main.py
# Usage from console.py: sudo python3 console.py

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

tenant_id = None
# vpc_id = None

def login(message = True, choice = None):
    global tenant_id
    # click.echo()
    if message:
        click.secho("1: Create New User", fg='cyan')
        click.secho("2: Login to Existing Account", fg='cyan')
        click.secho("3: Exit", fg='cyan')
        choice = click.prompt(click.style("Please enter your choice \U0001F50D", fg='yellow'), type=int)
    if choice == 1:
        tenantName = click.prompt(click.style("Please enter the tenant name", fg='yellow'), type=str)
        if tenantName == 'exit':
            login()
        tenant = Tenant.find_by_name(db, tenantName)
        if not tenant:
            tenant = Tenant(tenantName).save(db)
            message = "\nTenant is created successfully!!"
            click.secho(message, fg='green') 
            tenant_id = tenant.get_id()
            home()
        else:
            message = "\nThere is a tenant with this name already, please provide a different name"
            click.secho(message, fg='red')
            click.secho("Try again, enter 'exit' to leave prompt", fg="yellow")
            login(message=False, choice=choice)
    elif choice == 2:
        tenantName = click.prompt(click.style("Enter your User ID: ", fg='yellow'), type=str)
        if tenantName == 'exit':
            login()
        tenant = Tenant.find_by_name(db, tenantName)
        if not tenant:
            message = "There is no tenant with this name, please provide a different name.."
            click.secho(message, fg='red')
            click.secho("Try again, enter 'exit' to leave prompt", fg="yellow")
            login(message=False, choice=choice)
        tenant_id = tenant.get_id()
        click.secho('\n')
        home()
    elif choice == 3:
        click.secho("Good bye! \U0001F44B \U0001F44B", fg='green')
        exit()
    else:
        click.secho("Invalid choice. Please try again.. \U0000274C", fg='red')
        login()
    click.echo()

def display_welcome(title = pyfiglet.figlet_format("- MIXXCLOUD -", font="slant"), message="Welcome to the Cloud Implementation by Sumalatha, Thomas, Karan & Deepak!! \U0001F44B \U0001F44B"):
    click.secho(title, fg='blue', bold=True)
    click.secho(message, fg='white', bold=True)
    click.echo()
    click.echo()

def home():
    global tenant_id
    click.secho("1: List Resources", fg='cyan')
    click.secho("2: VPC", fg='cyan')
    click.secho("3: Servers", fg='cyan')
    click.secho("9: Log out", fg='cyan')
    choice = click.prompt(click.style("Please enter your choice \U0001F50D", fg='yellow'), type=int)
    if choice == 1:
        pass
    elif choice == 2:
        vpc_home()
    elif choice == 9:
        tenant_id = None
        login()
        return
    else:
        click.secho("Invalid Choice selected", fg='red')
        home()

def vpc_home(message = True, choice = None):
    global tenant_id
    # global vpc_id
    tenant = Tenant.find_by_id(db, tenant_id)
    vpc_data = {}
    
    for vpcid in tenant.vpcs:
        vpc = VPC.find_by_id(db, vpcid)
        vpc_data[vpc.name] = vpc.get_id()
    
    if message:
        print('\n')
        if len(vpc_data) != 0:
            click.secho(f"Available VPCs", fg='cyan')    
            for vpc_name in vpc_data:
                click.secho(f"{vpc_name}", fg='green')
        click.secho("1: Create VPC", fg='cyan')
        click.secho("2: List VPCs", fg='cyan')
        click.secho("3: VPC Details", fg='cyan')
        click.secho("4: Delete VPC", fg='cyan')
        click.secho("9: Exit Menu", fg='cyan')
    if choice is None:
        choice = click.prompt(click.style("Please enter your choice", fg='yellow'), type=int)
    if choice == 1:
        # Create VPC Here
        # VPCController.create_subnet_in_container(db, )
        vpc_name = click.prompt(click.style("Enter VPC Name", fg='yellow'), type=str)
        if vpc_name == 'exit':
            vpc_home()
        tenant = Tenant.find_by_id(db, tenant_id)
        if vpc_name in vpc_data.keys():
            click.secho("VPC Already exits", fg='red')
            click.secho("Enter 'exit' to leave menu", fg='yellow')
            vpc_home(message=False, choice=choice)
        else: 
            click.secho("Creating VPC", fg='green')
            TenantController.create_vpc(db, tenant, vpc_name)
            vpc_home()
    elif choice == 2:
        if len(vpc_data) != 0:
            click.secho(f"Available VPCs", fg='cyan')    
            for vpc_name in vpc_data:
                click.secho(f"{vpc_name}", fg='green')
        else:
            click.secho(f"No available VPCs", fg='red') 
        vpc_home(message=False)
    elif choice == 3:
        vpc_name = click.prompt(click.style("Enter VPC Name", fg='yellow'), type=str)
        if vpc_name == 'exit':
            vpc_home()
        vpc_id = vpc_data.get(vpc_name, None)
        if vpc_id is None:
            click.secho(f"Choosen VPC not found", fg='red') 
            click.secho(f"Try again, type 'exit' to exit", fg='red') 
            vpc_home(message=False, choice=choice)
        # VPC is selected
        # vpc = VPC.find_by_id(db, vpc_id)
        else:
            vpc_detail(vpc_id = vpc_id)
    elif choice == 4:
        vpc_name = click.prompt(click.style("Enter VPC Name", fg='yellow'), type=str)
        if vpc_name not in vpc_data:
            click.secho("VPC not found", fg='cyan')
        tenant = Tenant.find_by_id(db, tenant_id)
        TenantController.delete_vpc(db, tenant, vpc_data[vpc_name])
        vpc_home()
    elif choice == 9:
        home()
        return
    else:
        click.secho("Incorrect option selected", fg='red')
        vpc_home(message = False)
        
def vpc_detail(message=True, choice=None, vpc_id = None):
    # global vpc_id
    def check_overlap(cidr):
        nw = ip_network(cidr)
        for _sb_id in vpc.subnets:
            _sb = Subnet.find_by_id(db, _sb_id)
            if nw.overlaps(_sb.get_ipobj()):
                click.secho("CIDR Ranges overlaps with existsing subnets", fg='red')
                raise Exception("")
    vpc = VPC.find_by_id(db, vpc_id)
    loadbalancer_exists = True if vpc.lbs else False
    
    subnets_data = {}
    for sb_id in vpc.subnets:
        sb = Subnet.find_by_id(db, sb_id)
        subnets_data[sb.network_name] = sb_id
    
    if message:
        click.secho("1: List Subnets", fg='cyan')
        click.secho("2: List Servers", fg='cyan')
        click.secho("3: Create Subnet", fg='cyan')
        click.secho("4: Delete Subnet", fg='cyan')
        click.secho("5: Create Server", fg='cyan')
        click.secho("6: Delete Server", fg='cyan')
        if loadbalancer_exists:
            click.secho("7: List Load Balancer Details", fg='cyan')
            click.secho("8: Delete Load Balancer", fg='cyan')
            click.secho("9: Add targets ips", fg='cyan')
            click.secho("10: Delete targets ips", fg='cyan')
        else: 
            click.secho("7: Create Load Balancer", fg='cyan')
            
        click.secho("11: Exit Menu", fg='cyan')

    if choice is None:
        choice = click.prompt(click.style("Please enter your choice", fg='yellow'), type=int)
    if choice == 1:
        if len(subnets_data) > 0:
            click.secho("Subnets Details", fg='cyan')
            for _nw_name, _sb_id in subnets_data.items():
                _sb = Subnet.find_by_id(db, _sb_id)
                # subnets_data[sb.network_name] = sb_id
                click.secho(f"    {_nw_name}\t\t{_sb.cidr}", fg='green')
        else:
            click.secho("No subnets found", fg='red')
        vpc_detail(message=False, vpc_id=vpc_id)
    elif choice == 2:
        _servers = db.container.find({"vpc_id": vpc_id})
        flag = True
        for _server in _servers:
            if flag: 
                click.secho("Server details", fg='cyan')
                flag = False
            ser = Container.from_dict(_server)
            click.secho(f"    {ser.name}", fg='cyan')
            for _int in ser.interfaces:
                _ip = Interface.find_by_id(db, _int)
                _sb = Subnet.find_by_id(db, _ip.subnet_id)
                click.secho(f"        {_sb.network_name} - {_ip.ip_address}", fg='green')
        
        if flag:
            click.secho("No servers found", fg='red')
            vpc_detail(message=False, vpc_id=vpc_id)
        vpc_detail(vpc_id=vpc_id, message= False)
            
    elif choice == 3:
        print("vpc_id", vpc_id)
        subnet_name = click.prompt(click.style("Enter Subnet name", fg='yellow'), type=str)
        cidr = click.prompt(click.style("Enter CIDR", fg='yellow'), type=str)
        try:
            check_overlap(cidr)
        except:
            while True:
                click.secho("Entered CIDR was invalid", fg='red')
                click.secho("Try again", fg='red')
                try:
                    cidr = click.prompt(click.style("Enter CIDR", fg='yellow'), type=str)
                    check_overlap(cidr)
                except:
                    pass
        print(vpc_id)
        VPCController.create_subnet_in_container(db, vpc_id, subnet_name, cidr)
        vpc_detail(vpc_id=vpc_id)
    elif choice == 4:
        # Display available subnets
        subnet_name = click.prompt(click.style("Enter Subnet name", fg='yellow'), type=str)
        VPCController.delete_subnet_in_container(db, vpc_id, subnet_name)
        vpc_detail(vpc_id=vpc_id)
    elif choice == 5:
        subnet_name = click.prompt(click.style("Enter Subnet name", fg='yellow'), type=str)
        if subnet_name not in subnets_data:
            click.secho("Subnet not found, exiting...", fg='red')
            vpc_detail(vpc_id=vpc_id)
        container_name = click.prompt(click.style("Enter Container name", fg='yellow'), type=str)
        container_image = click.prompt(click.style("Enter docker image", fg='yellow'), type=str)
        click.secho("Avaiable Regions:", fg='cyan')
        click.secho("east", fg='green')
        click.secho("west", fg='green')
        region = click.prompt(click.style("Enter region", fg='yellow'), type=str)
        vcpu = click.prompt(click.style("Enter vCPUs", fg='yellow'), type=int)
        mem = click.prompt(click.style("Enter memory (Ex: 2048m)", fg='yellow'), type=str)
        cont = Container(container_name, container_image, region, vcpu, mem, vpc_id=vpc_id).save(db)
        ContainerController.create(db, cont.get_id())
        default_route = IPUtils.get_default_subnet_gateway(db, subnets_data[subnet_name], cont.region)
        ContainerController.connect_to_network(db, cont.get_id(), subnets_data[subnet_name], default_route)
        vpc_detail(vpc_id=vpc_id)
    elif choice == 6:
        # List all containers
        conatiner_data = {}
        containers = db.container.find({'vpc_id': vpc_id})
        for _c in containers:
            container = Container.from_dict(_c)
            conatiner_data[container.name] = container.get_id()
        if len(conatiner_data) > 0:
            click.secho("Available containers", fg='cyan')
            for name in conatiner_data:
                click.secho(f"{name}", fg='green')
        else:
            click.secho("No Containers available for deletion", fg='red')
            vpc_detail(vpc_id=vpc_id)
            return 
        container_name = click.prompt(click.style("Enter Container name", fg='yellow'), type=str)
        if container_name not in conatiner_data:
            click.secho("Invalid selection", fg='red')
            vpc_detail(vpc_id=vpc_id)
            return
        cont = Container.find_by_name(db, container_name)
        ContainerController.delete_container(db, vpc_id, cont.get_id())
        vpc_detail(vpc_id=vpc_id)
    elif choice == 7:
        if loadbalancer_exists:
            lbs = list(vpc.lbs.keys())
            lb = LoadBalancer.find_by_id(db, vpc.lbs[lbs[0]])
            click.secho(f" Name: {lb.name}", fg='cyan')
            click.secho(f"  Public IP: {lb.lb_ip}", fg='cyan')
            click.secho(f"  Target IPs", fg='cyan')
            _txt = 'IaaS' if lb.type == LBType.IAAS else 'LBaaS'
            click.secho(f"  LB Type: {_txt}", fg='cyan')
            for ip in lb.target_group:
                click.secho(f"IP: {ip['ip']}\t Weight: {ip['weight']}", fg='green')
            if len(lb.target_group) == 0:
                click.secho(f"    No target ips", fg='yellow')
            vpc_detail(vpc_id=vpc_id, message=False)
        else:
            # Create lb
            pub_sb = Subnet.find_by_name(db, HOST_PUBLIC_NETWORK)
            ip = IPUtils.get_unique_ip_from_region(db, pub_sb.get_id(), 'east')
            lb_name = click.prompt(click.style("Enter Load Balancer name", fg='yellow'), type=str)
            click.secho(f"Select type of load balancer", fg='cyan')
            click.secho(f"1. Load balancing through infrastructure", fg='green')
            click.secho(f"2. Load balancing as a Service", fg='green')
            lb_type = click.prompt(click.style("Enter Load Balancer name", fg='yellow'), type=int)
            if lb_type == 1:
                lb_type = LBType.IAAS
            elif lb_type == 2:
                lb_type = LBType.VM
            else:
                click.secho(f"Invalid option selected", fg='red')
                vpc_detail(vpc_id=vpc_id)
                return
            ContainerController.create_load_balancer(db, tenant_id, vpc_id, lb_name, ip, lb_type)
            vpc_detail(vpc_id=vpc_id)
    elif choice == 8:
        conf = click.prompt(click.style("Are you sure you want to delete the load balancer? (y/N)", fg='red'), type=str)
        if conf != 'y':
            click.secho(f"Deletion cancelled", fg='green')
            vpc_detail(vpc_id=vpc_id)
            return
        lbs = list(vpc.lbs.keys())
        lb = LoadBalancer.find_by_id(db, vpc.lbs[lbs[0]])
        
        ContainerController.delete_loadbalancer(db, tenant_id, vpc_id, lb.name)
        vpc_detail(vpc_id=vpc_id)
        
    elif choice == 9:
        _servers = db.container.find({"vpc_id": vpc_id,})
        flag = True
        for _server in _servers:
            if flag: 
                click.secho("Server details", fg='cyan')
                flag = False
            ser = Container.from_dict(_server)
            ser.name 
            
            click.secho(f"    {ser.name}", fg='cyan')
            for _int in ser.interfaces:
                _ip = Interface.find_by_id(db, _int)
                _sb = Subnet.find_by_id(db, _ip.subnet_id)
                click.secho(f"        {_sb.network_name} - {_ip.ip_address}", fg='green')
        if flag:
            click.secho("No servers found", fg='red')
        click.secho("Registered Ips", fg='cyan')
        # add ips
        lbs = list(vpc.lbs.keys())
        lb = LoadBalancer.find_by_id(db, vpc.lbs[lbs[0]])
        click.secho(f"Target IPs", fg='cyan')
        _txt = "IaaS" if lb.type == LBType.IAAS else "LBaaS"
        click.secho(f"LB Type: {_txt}", fg='cyan')
        for ip in lb.target_group:
            click.secho(f"IP: {ip.ip}\t Weight: {ip.weight}", fg='green')
        ip_addresses = []
        # ip_address, weight
        while True:
            ip_address = click.prompt(click.style("Enter ip address of server", fg='yellow'), type=str)
            weight = click.prompt(click.style("Enter weight", fg='yellow'), type=int)
            ip_addresses.append({"ip_address": ip_address, "weight": weight})
            add_more = click.prompt(click.style("Add more (y/n)", fg='yellow'), type=str)
            if add_more != 'y':
                break
        print(tenant_id, vpc_id, vpc.lbs[lbs[0]], ip_addresses)
        lb = LoadBalancer.find_by_id(db, vpc.lbs[lbs[0]])
        ContainerController.add_ip_targets(db, tenant_id, vpc_id, lb.name, ip_addresses)
        vpc_detail(vpc_id=vpc_id)
    elif choice == 10:
        # delete ips
        lbs = list(vpc.lbs.keys())
        lb = LoadBalancer.find_by_id(db, vpc.lbs[lbs[0]])
        click.secho(f"Target IPs", fg='cyan')
        _txt = "IaaS" if lb.type == LBType.IAAS else "LBaaS"
        click.secho(f"LB Type: {_txt}", fg='cyan')
        for ip in lb.target_group:
            click.secho(f"IP: {ip.ip}\t Weight: {ip.weight}", fg='green')
        
        ip_addresses = []
        # ip_address, weight
        while True:
            ip_address = click.prompt(click.style("Enter ip address of server", fg='yellow'), type=str)
            ip_addresses.append(ip_address)
            add_more = click.prompt(click.style("Add more (y/n)", fg='yellow'), type=str)
            if add_more != 'y':
                break
        ContainerController.remove_ip_tartgets(db, tenant_id, vpc_id, vpc.lbs[lbs[0]], ip_addresses)
        vpc_detail(vpc_id=vpc_id)
    elif choice == 11:
        vpc_id = None
        vpc_home()
    else:
        click.secho(f"Invalid option selected", fg='red')
        vpc_detail(message=False, vpc_id=vpc_id)
if __name__ == "__main__":
    display_welcome()
    login()
    # console()
