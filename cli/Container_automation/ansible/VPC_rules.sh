/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.10 --dport 8080 -m statistic --mode random --probability 0.33 -j DNAT --to-destination 10.3.2.12:80
/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.10 --dport 8080 -m statistic --mode random --probability 0.33 -j DNAT --to-destination 10.3.2.15:80
/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.10 --dport 8080 -m statistic --mode random --probability 0.5 -j DNAT --to-destination 10.3.2.13:80
/sbin/iptables -A PREROUTING -t nat -p tcp -d 10.10.10.10 --dport 8080 -m statistic --mode random --probability 1 -j DNAT --to-destination 10.3.2.16:80
