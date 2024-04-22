FROM ubuntu:22.04

RUN apt update && apt install git sudo python3 vim net-tools inetutils-ping iproute2 openssh-server iptables dnsmasq arping -y
RUN git clone https://github.com/yoche2000/my-vrrp.git

# RUN mv my-vrrp/ /app/

CMD tail -f /dev/null