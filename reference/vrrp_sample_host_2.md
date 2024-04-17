This file contains sample scripts for vrrp in multiple hosts


```
vrrp_instance VI_1 {
    interface C2pubinf
    state BACKUP
    virtual_router_id 1
    priority 101
    advert_int 2
    unicast_src_ip 172.16.1.6 #IP of this device
    unicast_peer{
        172.16.1.7 #IP of peer device
    }
    authentication {
        auth_type AH
        auth_pass monkey
    }
    virtual_ipaddress {
        10.10.10.6/24 dev C2pubinf label C2pubinf:vip
    }
}
```

```
vrrp_instance VI_2 {
    interface C2pubinf
    state MASTER
    virtual_router_id 1
    priority 101
    advert_int 2
    unicast_src_ip 172.16.1.7 #IP of this device
    unicast_peer{
        172.16.1.6 #IP of peer device
    }
    authentication {
        auth_type AH
        auth_pass monkey
    }
    virtual_ipaddress {
        10.10.10.6/24 dev C2pubinf label C2pubinf:vip
    }
}
```

```sh
sudo ip netns exec C2 keepalived -f /etc/keepalived/keepalived-C2.conf
```