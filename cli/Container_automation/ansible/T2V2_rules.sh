/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.5 --dport 8080 -m statistic --mode random --probability 0.5 -j DNAT --to-destination 192.168.30.3:80
/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.5 --dport 8080 -m statistic --mode random --probability 1.0 -j DNAT --to-destination 192.168.30.5:80
/sbin/iptables -t nat -A POSTROUTING -s 10.10.10.0/24 -j SNAT --to-source 192.168.30.2