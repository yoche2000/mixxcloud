import os
import ipaddress
import subprocess

def newNet (networkID, bridgeID, cidr):
    template_path = '/etc/libvirt/qemu/networks/subnets/subnet_template.xml'
    newpath = '/etc/libvirt/qemu/networks/subnets/' + networkID + '.xml'
    netmask = cidr.netmask
    hosts = list(cidr.hosts())

    with open(template_path, 'r') as file:
        data = file.read()
        v = {'NETWORKNAME': networkID,
             'BRIDGENAME': bridgeID, 
             'ROUTERIP': hosts[0], 
             'NETMASK': cidr.netmask, 
             'HOSTIPSTART': hosts[1],
             'HOSTIPEND': hosts[-1]
             }
        
        for key in v.keys():
            data = data.replace(key, str(v[key]))

    f = open(newpath, 'w')
    f.write(data)
    f.close()

    os.system("sudo virsh net-define "+newpath)
    os.system("sudo virsh net-start "+networkID)

def showNet(networkID):
    os.system("sudo virsh net-info "+networkID)

def rmNet(networkID):
    path = '/etc/libvirt/qemu/networks/subnets/' + networkID + '.xml'
    os.system("sudo rm "+path)
    os.system("sudo virsh net-undefine "+networkID)
    os.system("sudo virsh net-destroy "+networkID)


def isRunning(networkID):
    t = subprocess.check_output("sudo virsh net-list --all", shell=True)
    if networkID in str(t):
        return True
    else:
        return False


