#!/bin/bash
sudo /sbin/iptables -t nat -A POSTROUTING -o enp1s0 -j MASQUERADE
sudo /sbin/iptables -A FORWARD -i enp2s0 -o enp1s0 -j ACCEPT
sudo /sbin/iptables -A FORWARD -i enp1s0 -o enp2s0 -m state --state RELATED,ESTABLISHED -j ACCEPT