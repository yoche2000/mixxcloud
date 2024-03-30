import click
import shutil
import pyfiglet
from controllers.tenant_controller import TenantController
from models.db_model import DB
import traceback
# sudo apt-get install -y python3-pyfiglet
# Usage from main.py: sudo python3 main.py [command]
# Usage from console.py: sudo python3 console.py [command]

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
    tenantName = click.prompt(click.style("Enter your User ID: ", fg='yellow'), type=str)
    click.echo()

def display_welcome(title = pyfiglet.figlet_format("- MIXXCLOUD -", font="slant"), message="Welcome to the Cloud Implementation by Sumalatha, Thomas, Karan & Deepak!! \U0001F44B \U0001F44B"):
    click.secho(title, fg='blue', bold=True)
    click.secho(message, fg='white', bold=True)
    click.echo()
    click.echo()

@click.group()
def cli():
    pass

@cli.command()
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
        pass
    elif choice == 2:
        pass
    elif choice == 3:
        pass
    else:
        click.secho("Invalid choice. Please try again.. \U0000274C", fg='red')

@cli.command()
def tenant():
    display_welcome(title = pyfiglet.figlet_format("- Tenant Console -", font="digital"), message="Choose an action to continue:")
    click.secho("1: Create Tenant", fg='cyan')
    click.secho("2: Delete Tenant", fg='cyan')
    click.secho("3: List VPCs", fg='cyan')
    click.secho("4: List Subnets", fg='cyan')
    click.secho("5: List VMs", fg='cyan')


@cli.command()
def vpc():
    display_welcome(title = pyfiglet.figlet_format("- VPC Console -", font="digital"), message="Choose an action to continue:")
    print(f"Tenant Name:", tenantName)
    click.secho("1: Create VPC", fg='cyan')
    click.secho("2: Attach Subnet to VPC", fg='cyan')
    click.secho("3: Detach Subnet to VPC", fg='cyan')
    click.secho("4: Delete VPC", fg='cyan')
    click.secho("5: List VPCs", fg='cyan')
    click.secho("6: Create Subnet", fg='cyan')
    click.secho("7: Delete Tenant", fg='cyan')

    # Create VPC
    click.echo()
    choice = click.prompt(click.style("Please enter your choice \U0001F50D", fg='yellow'), type=int)

    if choice == 1:
        """
        # Check the Controller Files
        # Ask for inputs
        TenantController.create_vpc(db, tenantname, vpcname, region)
        """  
        pass 
    else:
        pass

@cli.command()
def loadbalancer():
    display_welcome(title = pyfiglet.figlet_format("- Load Balancer Console -", font="digital"), message="Choose an action to continue:")

def main():
    display_welcome()
    login()
    cli()

if __name__ == "__main__":
    main()
