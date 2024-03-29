import click
import shutil
import pyfiglet
# sudo apt-get install -y python3-pyfiglet
# Usage from main.py: sudo python3 main.py [command]
# Usage from console.py: sudo python3 console.py [command]


def display_welcome(title = pyfiglet.figlet_format("- MIXXCLOUD -", font="slant"), message="Welcome to the Cloud Implementation by Suma, Thomas, Karan & Deepak!! \U0001F44B \U0001F44B"):
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
    click.secho("2: Read VM", fg='cyan')
    click.secho("3: Update VM", fg='cyan')
    click.secho("4: Delete VM", fg='cyan')
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

@cli.command()
def vpc():
    display_welcome(title = pyfiglet.figlet_format("- VPC Console -", font="digital"), message="Choose an action to continue:")

@cli.command()
def subnet():
    display_welcome(title = pyfiglet.figlet_format("- Subnet Console -", font="digital"), message="Choose an action to continue:")

@cli.command()
def loadbalancer():
    display_welcome(title = pyfiglet.figlet_format("- Load Balancer Console -", font="digital"), message="Choose an action to continue:")

def main():
    display_welcome()
    cli()

if __name__ == "__main__":
    main()
