# Setting up BRSN1
sudo brctl addbr BRSN1
sudo ip link set BRSN1 up

Create a net.xml
```sh
<network>
  <name>BRSN1-nw</name>
  <forward mode='bridge'/>
  <bridge name='BRSN1'/>
</network>
```

#Create namespace
sudo ip netns add NS-T1V1E

# Creating veth pair
sudo ip link add T1V1SN1R type veth peer name T1V1SN1B
sudo brctl addif BRSN1 T1V1SN1B

sudo ip link set T1V1SN1R netns NS-T1V1W
sudo ip link set T1V1SN1R netns NS-T1V1E

sudo ip link set T1V1SN1B up
sudo ip netns exec NS-T1V1W  ip link set T1V1SN1R up

sudo ip link add T1V1SN2R type veth peer name T1V1SN2B
sudo ip link set T1V1SN1B up
sudo ip link set T1V1SN2R netns NS-T1V1E
sudo ip netns exec NS-T1V1E  ip link set T1V1SN2R up

# Define a VM connected to this bridge
.16 system VM1
vms:
- vm_name: VM1
  vcpu: 1
  mem: 1024
  disk_size: 10G
  interfaces:
  - network_name: BRSN1-nw
    iface_name: enp1s0
    ipaddress: 192.168.1.200/24
    dhcp: false
    gateway: 192.168.1.1


.17 system VM2
vms:
- vm_name: VM2
  vcpu: 1
  mem: 1024
  disk_size: 10G
  interfaces:
  - network_name: BRSN1-nw
    iface_name: enp1s0
    ipaddress: 192.168.1.100/24
    dhcp: false
    gateway: 192.168.1.2




# Enable nat on namespaces
sudo ip netns exec NS-T1V1W iptables -t nat -A POSTROUTING -j MASQUERADE
sudo ip netns exec NS-T1V1E iptables -t nat -A POSTROUTING -j MASQUERADE