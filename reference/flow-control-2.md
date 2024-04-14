#host 192.168.38.17
# create NS router for T1V1
sudo ip netns add NS-T1V1W
sudo ip netns exec NS-T1V1W ip link set lo up

# link setup between host and NS
sudo ip link add T1V1V type veth peer name T1V1B
sudo ip link set T1V1V netns NS-T1V1W
sudo ip netns exec NS-T1V1W ip link set T1V1V up
sudo ip netns exec NS-T1V1W ip addr add 172.16.0.102/12 dev T1V1V
sudo brctl addif Tw2 T1V1B
sudo ip link set T1V1B up
sudo ip netns exec NS-T1V1W ip route add default via 172.16.0.2

# create SN1 infra in NS
sudo ip netns exec NS-T1V1W brctl addbr BRSN1R
sudo ip netns exec NS-T1V1W ip link set BRSN1R up
sudo ip netns exec NS-T1V1W ip addr add 192.168.1.2/24 dev BRSN1R

### link setup between SN1 and NS
sudo ip link add T1V1SN1R type veth peer name T1V1SN1B
sudo ip link set T1V1SN1R netns NS-T1V1W
sudo ip netns exec NS-T1V1W brctl addif T1V1SN1R
sudo ip netns exec NS-T1V1W brctl addif BRSN1R T1V1SN1R

### create VXLAN for SN1 (VNI10, local 102, remote 101)
sudo ip netns exec NS-T1V1W ip link add VX-SN1 type vxlan id 10 local 172.16.0.102 remote 172.16.0.101
sudo ip netns exec NS-T1V1W ip link set up VX-SN1
sudo ip netns exec NS-T1V1W brctl addif BRSN1R VX-SN1
sudo ip netns exec NS-T1V1W bridge fdb append 00:00:00:00:00:00 dev VX-SN1 dst 172.16.0.101


#host 192.168.38.16
# create NS router for T1V1
sudo ip netns add NS-T1V1E
sudo ip netns exec NS-T1V1W ip link set lo up

# link setup between host and NS
sudo ip link add T1V1V type veth peer name T1V1B
sudo ip link set T1V1V netns NS-T1V1E
sudo ip netns exec NS-T1V1E ip link set T1V1V up
sudo ip netns exec NS-T1V1E ip addr add 172.16.0.101/12 dev T1V1V
sudo brctl addif Tw1 T1V1B
sudo ip link set T1V1B up
sudo ip netns exec NS-T1V1E ip route add default via 172.16.0.1

# create SN1 infra in NS
sudo ip netns exec NS-T1V1E brctl addbr BRSN1R
sudo ip netns exec NS-T1V1E ip link set BRSN1R up
sudo ip netns exec NS-T1V1E ip addr add 192.168.1.1/24 dev BRSN1R

### link setup between SN1 and NS
sudo ip link add T1V1SN1E type veth peer name T1V1SN1B
sudo ip link set T1V1SN1E netns NS-T1V1W
sudo ip netns exec NS-T1V1E brctl addif BRSN1R T1V1SN1R

### create VXLAN for SN1 (VNI10, local 101, remote 102)
sudo ip netns exec NS-T1V1E ip link add VX-SN1 type vxlan id 10 local 172.16.0.101 remote 172.16.0.102
sudo ip netns exec NS-T1V1E ip link set up VX-SN1
sudo ip netns exec NS-T1V1E brctl addif BRSN1R VX-SN1
sudo ip netns exec NS-T1V1E bridge fdb append 00:00:00:00:00:00 dev VX-SN1 dst 172.16.0.102