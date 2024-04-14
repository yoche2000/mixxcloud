# define bridges in the host 

sudo ip link add T1EP1B type veth peer name T1EP1R
sudo ip link set T1EP1R netns NS-T1V1W
sudo ip link set T1EP1B up
sudo ip netns exec NS-T1V1W  ip link set T1EP1R up

sudo ip link add T1EP1B type veth peer name T1EP1R
sudo ip link set T1EP1R netns NS-T1V1E
sudo ip link set T1EP1B up
sudo ip netns exec NS-T1V1E  ip link set T1EP1R up

sudo brctl addif host-pub-br T1EP1B
sudo brctl addif Tw2 T1EP1B

sudo ip netns exec NS-T1V1W ip addr add 10.10.10.123/24 dev T1EP1R
sudo ip netns exec NS-T1V1E ip addr add 10.10.10.122/24 dev T1EP1R

# Check status
ip addr show T1EP1B
sudo ip netns exec NS-T1V1W ip addr show T1EP1R
ip addr show T1EP1B

sudo ip netns exec NS-T1V1W ip addr delete 10.10.10.123/24 dev T1EP1R
sudo ip netns exec NS-T1V1E ip addr delete 10.10.10.123/24 dev T1EP1R