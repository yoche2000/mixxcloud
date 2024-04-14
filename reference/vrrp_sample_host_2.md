This file contains sample scripts for vrrp in multiple hosts


```
vrrp_instance VI_1 {
    interface T1EP1R
    state MASTER
    virtual_router_id 1
    priority 101
    advert_int 2
    unicast_src_ip 172.16.0.102 #IP of this device
    unicast_peer{
        172.16.0.101 #IP of peer device
    }
    authentication {
        auth_type AH
        auth_pass monkey
    }
    virtual_ipaddress {
        10.10.10.123/24 dev T1EP1R label T1EP1R:vip
    }
}
```

```
vrrp_instance VI_1 {
    interface T1EP1R
    state MASTER
    virtual_router_id 1
    priority 101
    advert_int 2
    unicast_src_ip 172.16.0.101 #IP of this device
    unicast_peer{
        172.16.0.102 #IP of peer device
    }
    authentication {
        auth_type AH
        auth_pass monkey
    }
    virtual_ipaddress {
        10.10.10.123/24 dev T1EP1R label T1EP1R:vip
    }
}
```

```sh
sudo ip netns exec NS-T1V1W keepalived -f /etc/keepalived/keepalived-T1V1.conf
```