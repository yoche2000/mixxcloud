/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.3 --dport 8080 -m statistic --mode random --probability 0.5 -j DNAT --to-destination 10.20.30.4:80
/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.3 --dport 8080 -m statistic --mode random --probability 1.0 -j DNAT --to-destination 10.20.30.6:80
/sbin/iptables -t nat -A POSTROUTING -s 10.10.10.0/24 -j SNAT --to-source 10.20.30.2