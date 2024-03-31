import click
import shutil
import pyfiglet
from controllers.tenant_controller import TenantController
from controllers.subnet_controller import SubnetController
from controllers.vpc_controller import VPCController
from controllers.vm_controller import VMController
from models.tenant_model import Tenant
from models.vpc_model import VPC
from models.vm_model import VM
from models.subnet_model import Subnet
from models.interface_model import Interface
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
            message = "There is no tenant with this name, please provide a different name.."
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
        network = click.prompt(click.style("Enter  subNetwork name for the VM: ", fg='yellow'), type=str)
        subnetId = Subnet.find_by_name(db,network).get_id()
        vm = VM(vmName,vCPU,vMem,disk_size,vpcId).save(db)
        vmId = vm.find_by_name(db,vmName).get_id()
        #VMController.define(db,vmId.get_id())
        VMController.connect_to_network(db,vpcId,subnetId,vmId,default=True)
        VMController.start(db, vmId)
        
    elif choice == 2:
        vmName = click.prompt(click.style("Enter your VM name: ", fg='yellow'), type=str)
        vmId = VM.find_by_name(db,vmName)
        vpcId = vmId.vpc_id
        vpcName = VPC.find_by_id(db, vpcId)
        subnetList = VPCController.list_subnets(db,vpcName)
        click.secho(f"Subnets available are:", fg='cyan')
        for subnet in subnetList:
            print(subnet.network_name + ": " + subnet.subnet)
        click.secho(f"Choose to attach the VM to any of the above subnets..", fg='cyan')
        network = click.prompt(click.style(f"Enter SubNetwork name from the VPC - {vpcId}, you want to add for the VM: ", fg='yellow'), type=str)
        subnetId = Subnet.find_by_name(db,network).get_id()
        VMController.connect_to_network(db,vpcId,subnetId,vmId.get_id())

    elif choice == 3:
        vmName = click.prompt(click.style("Enter your VM name: ", fg='yellow'), type=str)
        vmId = VM.find_by_name(db,vmName)
        vpcId = vmId.vpc_id
        network = click.prompt(click.style("Enter VPC network name you want to add for the VM: ", fg='yellow'), type=str)
        subnetId = Subnet.find_by_name(db,network).get_id()
        VMController.disconnect_from_network(db,vmId.get_id(),subnetId)

    elif choice == 4:
        vmName = click.prompt(click.style("Enter your VM name: ", fg='yellow'), type=str)
        vm = VM.find_by_name(db, vmName)
        VMController.undefine(db, vm.get_id())
        vm.delete(db)

    elif choice == 5:
        vmName = click.prompt(click.style("Enter your VM name: ", fg='yellow'), type=str)
        vm = VM.find_by_name(db, vmName)
        print(f"Vm Name is: {vm.name}")
        print(f"CPU of the VM is: {vm.vCPU}")
        print(f"Memory of the VM is: {vm.vMem}")
        print(f"Disk Size of the VM is: {vm.disk_size}")
        vpcId = vm.vpc_id
        vpcName = VPC.find_by_id(db,vpcId).name
        print(f"VPC name for which this VM belongs is: {vpcName}")
        print(f"State of the VM is: {vm.state.name}")
        Interfaces = vm.interfaces
        print(f"Subnetworks of the VPC for which this VM is attached are: ")
        for interface in Interfaces:
            subnetID = Interface.find_by_id(db,interface).subnet_id
            networkName = Subnet.find_by_id(db,subnetID).network_name
            print(networkName)
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
       vpcName= tenantName+"-"+vpcName
       subnetList = VPCController.list_subnets(db,vpcName)
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
    click.secho("2: Create and Attach Subnet to VPC", fg='cyan')
    click.secho("3: Delete Subnet to VPC", fg='cyan')
    click.secho("4: Delete VPC", fg='cyan')
    click.secho("5: Main Console", fg='cyan')

    click.echo()
    choice = click.prompt(click.style("Please enter your choice \U0001F50D", fg='yellow'), type=int)

    if choice == 1:
        vpcName = click.prompt(click.style("Provide the VPC Name:", fg='yellow'), type=str)
        vpcName = tenantName+"-"+vpcName
        region = click.prompt(click.style("Provide the region of your choice:", fg='yellow'), type=str)
        if not TenantController.create_vpc(db, tenantName, vpcName, region):
            click.secho("VPC Configuation is UnSuccessful!! \U000026A0\U0000FE0F", fg='red')
            return -1
        vpc = TenantController.get_vpc_by_tenant_vpc_name(db, tenantName, vpcName)
        status = VPCController.up(db, tenantName, vpc)
        message = "VPC Creation is Successful!! \U00002714\U0000FE0F" if status is True else "VPC Creation is UnSuccessful!! \U000026A0\U0000FE0F" 
        click.secho(message, fg='red')
    elif choice == 2:
        vpcName = click.prompt(click.style("Provide the VPC Name where you want to create Subnet:", fg='yellow'), type=str)
        vpcName = tenantName+"-"+vpcName
        click.secho(f"VPC ID: {vpcName}", fg='green')
        subnetName = click.prompt(click.style("Provide the Sub-Network Name where you want to create Subnet:", fg='yellow'), type=str)
        subnetName = vpcName+"-"+subnetName
        click.secho(f"Subnet ID: {subnetName}", fg='green')
        bridgeName = subnetName+"-"+"br"
        click.secho(f"Bridge ID: {bridgeName}", fg='green')
        subnetCIDR = click.prompt(click.style("Provide the Subnet CIDR (ex: 192.168.10.0/24):", fg='yellow'), type=str)
        click.secho(f"Confirmed: {subnetCIDR}", fg='green')
        status = VPCController.create_subnet(db,tenantName, vpcName, subnetCIDR, subnetName, bridgeName)
        message = "Subnet Attachment is Successful!! \U00002714\U0000FE0F" if status is not None else "Subnet Attachment is UnSuccessful!! \U000026A0\U0000FE0F" 
        click.secho(message, fg='red')
    elif choice == 3:
        click.secho(f"This is a destructive operation! Ensure all the VMs are moved to different subnet/deleted..", fg='red')
        vpcName = click.prompt(click.style("Provide the VPC Name where you want to delete the Subnet:", fg='yellow'), type=str)
        vpcName = tenantName+"-"+vpcName
        click.secho(f"VPC ID: {vpcName}", fg='green')
        subnetName = click.prompt(click.style("Provide the Sub-Network Name to delete:", fg='yellow'), type=str)
        subnetName = vpcName+"-"+subnetName
        click.secho(f"Subnet ID: {subnetName}", fg='green')
        status = VPCController.remove_subnet(db, vpcName, subnetName)
        message = "Subnet Deletion is Successful!! \U00002714\U0000FE0F" if status is True else "Subnet Deletion is UnSuccessful!! \U000026A0\U0000FE0F" 
        click.secho(message, fg='red')
    elif choice == 4:
        vpcName = click.prompt(click.style("Provide the VPC Name which you want to delete:", fg='yellow'), type=str)
        vpcName = tenantName+"-"+vpcName
        subnetList = VPCController.list_subnets(db,vpcName)
        if len(subnetList) != 0:
            click.secho(f"VPC has multiple subnets..Delete them all first to delete this VPC..", fg='green')
            exit()
        vpcDownStatus = VPCController.down(db, tenantName, vpcName)
        if vpcDownStatus:
            click.secho(f"VPC is down, resources are undefined..", fg='green')
            routerVMStatus = VMController.undefine(db, f"RVM_{tenantName}_{vpcName}")
        else:
            click.secho(f"VPC is not down, failed", fg='red')
        if routerVMStatus:
            click.secho(f"Router VM is deleted..", fg='green')
        else:
            click.secho(f"Router VM failed to delete..", fg='red')
    elif choice == 5:
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
