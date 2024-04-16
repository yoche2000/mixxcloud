#!/bin/bash

# Update package list
apt update

# Install Apache and PHP
apt install -y apache2 php libapache2-mod-php

# Allow Apache through the firewall
ufw allow in "Apache"

# Create a PHP file to display the server IP
cat <<EOT > /var/www/html/ipinfo.php
<!DOCTYPE html>
<html>
<head>
    <title>Server IP Address</title>
</head>
<body>
    <h1>Server IP Address</h1>
    <p><?php echo \$_SERVER['SERVER_ADDR']; ?></p>
</body>
</html>
EOT

# Restart Apache to apply changes
systemctl restart apache2

# Echo a success message with instructions
echo "Apache and PHP have been installed, and the IP display page is set up."
echo "You can view your server IP by navigating to http://your_server_ip/ipinfo.php in a web browser."