/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.12 --dport 8080 -m statistic --mode random --probability 0.33 -j DNAT --to-destination 10.2.3.4:80
/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.12 --dport 8080 -m statistic --mode random --probability 0.5 -j DNAT --to-destination 10.2.3.5:80
/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.12 --dport 8080 -m statistic --mode random --probability 1 -j DNAT --to-destination 10.2.3.6:80
/sbin/iptables -t nat -A POSTROUTING -s 10.10.10.0/24 -j SNAT --to-source 10.2.3.8