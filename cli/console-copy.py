import click
import shutil
import pyfiglet
from models.vpc_model import VPC
from controllers.vm_controller import VMController
from models.vm_model import VM
from controllers.tenant_controller import TenantController
from controllers.vpc_controller import VPCController
from models.interface_model import Interface
from models.subnet_model import Subnet
from models.tenant_model import Tenant
from models.db_model import DB
import traceback
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

tenantName = None

def login():
    global tenantName
    click.echo()
    click.secho("1: Create New User-ID.", fg='cyan')
    click.secho("2: Login to Existing Account.", fg='cyan')
    click.secho("3: Exit", fg='cyan')
    choice = click.prompt(click.style("Please enter your choice \U0001F50D", fg='yellow'), type=int)
    if choice == 1:
        #print("Tenant Function will be called here..")
        tenantName = click.prompt(click.style("Please enter the tenant name", fg='yellow'), type=str)
        tenant = Tenant.find_by_name(db, tenantName)
        if not tenant:
            tenant = Tenant(tenantName).save(db)
            message = "Tenant is created successfully!!"
            click.secho(message, fg='red') 
        else:
            message = "There is a teant with this name already, please provide a different name"
            click.secho(message, fg='red')
        exit()
    elif choice == 2:
        tenantName = click.prompt(click.style("Enter your User ID: ", fg='yellow'), type=str)
        tenant = Tenant.find_by_name(db, tenantName)
        if not tenant:
            message = "There is no tenant with this name, please provide a different name"
            click.secho(message, fg='red')
            exit()
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

def vm():
    display_welcome(title = pyfiglet.figlet_format("- VM Console -", font="digital"), message="Choose an action to continue: \U0001F447")
    click.secho("1: Create VM", fg='cyan')
    click.secho("2: Attach VM to Subnet", fg='cyan')
    click.secho("3: Detach VM to Subnet", fg='cyan')
    click.secho("4: Delete VM", fg='cyan')
    click.secho("5: VM Info", fg='cyan')
    # Need to add more options, if required
    click.echo()
    choice = click.prompt(click.style("Please enter your choice \U0001F50D", fg='yellow'), type=int)

    if choice == 1:
        vpcName = click.prompt(click.style("Enter VPC Name for which you want to create a VM: ", fg='yellow'), type=str)
        vpcId = VPC.find_by_name(db,vpcName).get_id()
        vmName = click.prompt(click.style("Enter your VM name: ", fg='yellow'), type=str)
        vCPU = click.prompt(click.style("Enter vCPU for the VM: ", fg='yellow'), type=int)
        vMem = click.prompt(click.style("Enter vMem for the VM: ", fg='yellow'), type=int)
        disk_size = click.prompt(click.style("Enter disk_size for the VM: ", fg='yellow'), type=str)
        network = click.prompt(click.style("Enter VPC network name for the VM: ", fg='yellow'), type=str)
        subnetId = Subnet.find_by_name(db,network).get_id()
        vm = VM(vmName,vCPU,vMem,disk_size,vpcId)
        #vm.json()
        vm.save(db)
        vmId = vm.find_by_name(db,vmName).get_id()
        #VMController.define(db,vmId.get_id())
        VMController.connect_to_network(db,vpcId,subnetId,vmId,default=True)
        VMController.start(db, vmId)
        
    elif choice == 2:
        vmName = click.prompt(click.style("Enter your VM name: ", fg='yellow'), type=str)
        vmId = VM.find_by_name(db,vmName)
        vpcId = vmId.vpc_id
        network = click.prompt(click.style("Enter VPC network name you want to add for the VM: ", fg='yellow'), type=str)
        subnetId = Subnet.find_by_name(db,network).get_id()
        VMController.connect_to_network(db,vpcId,subnetId,vmId.get_id())

    elif choice == 3:
        vmName = click.prompt(click.style("Enter your VM name: ", fg='yellow'), type=str)
        vmId = VM.find_by_name(db,vmName)
        vpcId = vmId.vpc_id
        network = click.prompt(click.style("Enter VPC network name you want to add for the VM: ", fg='yellow'), type=str)
        subnetId = Subnet.find_by_name(db,network).get_id()
        VMController.disconnect_from_network(db,vmId.get_id(),subnetId)
    else:
        click.secho("Invalid choice. Please try again.. \U0000274C", fg='red')

def tenant():
    display_welcome(title = pyfiglet.figlet_format("- Tenant Console -", font="digital"), message="Choose an action to continue:")
    click.secho("1: Delete Tenant", fg='cyan')
    click.secho("2: List VPCs", fg='cyan')
    click.secho("3: List Subnets", fg='cyan')
    click.secho("4: List VMs", fg='cyan')

    # Create tenant
    click.echo()
    choice = click.prompt(click.style("Please enter your choice \U0001F50D", fg='yellow'), type=int)

    if choice == 1:
        tenant = Tenant.find_by_name(db, tenantName)
        print(tenant)
        if not tenant:
            message = "There is no tenant with this name, please try with the correct name"
            click.secho(message, fg='red')
        else:
            tenant.delete(db)
            message = "The given tenant and its associated VPCs have been deleted"
            click.secho(message, fg='red')
    elif choice == 2:
        VPCList = TenantController.list_vpcs(db, tenantName)
        for vpc in VPCList:
            print(vpc.name)   
    elif choice == 3:
       vpcName = click.prompt(click.style("Enter the vpc name for which you want to display Subnets ", fg='yellow'), type=str)
       subnetList = VPCController.list_subnets(db,vpcName)
       #print(subnetList)
       for subnet in subnetList:
            print(subnet.network_name + ": " + subnet.subnet)
    elif choice == 4:
        VPCList = TenantController.list_vpcs(db, tenantName)
        for vpc in VPCList:
            print(vpc.name + ": ") 
            VMs = db.vm.find({'vpc_id': vpc._id})
            for vm in VMs:
                print(vm.name)
        
def vpc():
    display_welcome(title = pyfiglet.figlet_format("- VPC Console -", font="digital"), message="Choose an action to continue:")
    click.secho("1: Create VPC", fg='cyan')
    click.secho("2: Attach Subnet to VPC", fg='cyan')
    click.secho("3: Detach Subnet to VPC", fg='cyan')
    click.secho("4: Delete VPC", fg='cyan')
    click.secho("5: List VPCs", fg='cyan')
    click.secho("6: Create Subnet", fg='cyan')
    click.secho("7: Delete Tenant", fg='cyan')
    click.secho("8: Main Console", fg='cyan')

    click.echo()
    choice = click.prompt(click.style("Please enter your choice \U0001F50D", fg='yellow'), type=int)

    if choice == 1:
        vpcName = click.prompt(click.style("Provide the VPC Name:", fg='yellow'), type=str)
        region = click.prompt(click.style("Provide the region of your choice:", fg='yellow'), type=str)
        if not TenantController.create_vpc(db, tenantName, vpcName, region):
            click.secho("VPC Configuation is UnSuccessful!! \U000026A0\U0000FE0F", fg='red')
            return -1
        vpc = TenantController.get_vpc_by_tenant_vpc_name(db, tenantName, vpcName)
        status = VPCController.up(db, tenantName, vpc)
        message = "VPC Creation is Successful!! \U00002714\U0000FE0F" if status is True else "VPC Creation is UnSuccessful!! \U000026A0\U0000FE0F" 
        click.secho(message, fg='red')
    elif choice == 2:
        pass
    elif choice == 8:
        console()
    else:
        click.secho("Invalid choice. Please try again.. \U0000274C", fg='red')
        console()

def loadbalancer():
    display_welcome(title = pyfiglet.figlet_format("- Load Balancer Console -", font="digital"), message="Choose an action to continue:")

def console():
    click.echo("----------------------------------------------------")
    command = click.prompt(click.style("Choose the console - vpc, vm, tenant, exit", fg='yellow'), type=str)
    click.echo()
    if command == "vpc":
        vpc()
    elif command == "vm":
        vm()
    elif command == "tenant":
        tenant()
    elif command == "exit":
        click.secho("Good bye! \U0001F44B \U0001F44B", fg='green')
        exit()
    else:
        click.secho("Invalid console chosen. Please try again.. \U0000274C", fg='red')
        console()

if __name__ == "__main__":
    display_welcome()
    login()
    console()
