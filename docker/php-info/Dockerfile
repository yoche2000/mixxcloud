# Use an official PHP image with Apache pre-installed
FROM --platform=linux/amd64 php:8.0-apache

# # Update packages and install PHP and Apache extensions
RUN apt-get update  && apt install net-tools sudo inetutils-ping iproute2 openssh-server iptables dnsmasq arping -y
    
RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 test

RUN  echo 'test:test' | chpasswd
# RUN apt upgrade

RUN service ssh start

# RUN libapache2-mod-php  
RUN rm -rf /var/lib/apt/lists/*

# Enable mod_rewrite for Apache
RUN ls -la /usr/sbin/ && a2enmod rewrite


# Copy a custom php file to display the server IP
COPY ipinfo.php /var/www/html/ipinfo.php

# Allow Apache through the firewall (handled differently in Docker, so typically not needed)
# But to illustrate, you could expose port 80
EXPOSE 80
EXPOSE 22

# The CMD directive is inherited from the base image, so Apache is already set to run
