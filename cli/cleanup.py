import click
import subprocess
from models.db_model import DB
import traceback
from constants.infra_constants import *
from models.subnet_model import Subnet, SubnetStatus, SubnetType
import test_run_ansible_playbook_for_vm_deletion as e

@click.group()
def cli():
    pass

@cli.command()
@click.argument('interface_names', nargs=-1)
def bridges(interface_names):
    """Bring network interfaces down and then delete them."""
    # sudo python script.py bridges br0 br1
    for interface_name in interface_names:
        # Bring the interface down
        try:
            subprocess.run(["sudo", "ip", "link", "set", interface_name, "down"], check=True)
            click.echo(f"The {interface_name} interface is now down.")
        except subprocess.CalledProcessError:
            click.echo(f"Failed to bring the {interface_name} interface down. Make sure you have the required permissions and the interface exists.")
            continue
        except Exception as e:
            click.echo(f"An error occurred when attempting to bring {interface_name} down: {str(e)}")
            continue
        try:
            subprocess.run(["sudo", "brctl", "delbr", interface_name], check=True)
            click.echo(f"The {interface_name} bridge has been deleted.")
        except subprocess.CalledProcessError:
            click.echo(f"Failed to delete the {interface_name} bridge. Ensure it exists and you have the correct permissions.")
        except Exception as e:
            click.echo(f"An error occurred when attempting to delete {interface_name} bridge: {str(e)}")

@cli.command()
@click.argument('network_names', nargs=-1)
def networks(network_names):
    """Bring down and delete network interfaces, then undefine and destroy virtual networks."""
    # sudo python script.py networks net1 net2
    for name in network_names:
        # Undefine the virtual network
        try:
            subprocess.run(["sudo", "virsh", "net-undefine", name], check=True)
            click.echo(f"The {name} virtual network has been undefined.")
        except subprocess.CalledProcessError:
            click.echo(f"Failed to undefine the {name} virtual network. Ensure it exists and you have the correct permissions.")
            continue
        except Exception as e:
            click.echo(f"An error occurred when attempting to undefine the {name} virtual network: {str(e)}")
            continue

        # Destroy the virtual network
        try:
            subprocess.run(["sudo", "virsh", "net-destroy", name], check=True)
            click.echo(f"The {name} virtual network has been destroyed.")
        except subprocess.CalledProcessError:
            click.echo(f"Failed to destroy the {name} virtual network. Ensure it exists and you have the correct permissions.")
        except Exception as e:
            click.echo(f"An error occurred when attempting to destroy the {name} virtual network: {str(e)}")

@cli.command()
def createdb():
    db1 = DB()
    try:
        client = db1.get_client()
    except Exception:
        traceback.print_exc()
        exit(1)
    db = client['ln']
    
    infra_sb = Subnet.find_by_name(db, HOST_NAT_NETWORK)
    if not infra_sb:
        print(f"Creating {HOST_NAT_NETWORK}")
        infra_sb = Subnet(HOST_NAT_SUBNET, HOST_NAT_NETWORK, HOST_NAT_BR_NAME, subnet_type = SubnetType.NAT.name).save(db)
    
    public_sb =  Subnet.find_by_name(db, HOST_PUBLIC_NETWORK)
    if not public_sb:
        print(f"Creating {HOST_PUBLIC_NETWORK}")
        public_sb = Subnet(HOST_PUBLIC_SUBNET, HOST_PUBLIC_NETWORK, HOST_PUBLIC_BR_NAME).save(db)
    print("Database is created with Infra Config..")

@cli.command()
def cleandb():
    db1 = DB()
    try:
        client = db1.get_client()
    except Exception:
        traceback.print_exc()
        exit(1)
    db = client.drop_database('ln')
    print("Database is dropped..")
    
@cli.command()
@click.argument('vm_names', nargs=-1)
def deletevms(vm_names):
    vms = []
    print("Delete VMs has been called..")
    for each in vm_names:
        vms.append(each)
    e.deletevms(vms)

if __name__ == "__main__":
    cli()
