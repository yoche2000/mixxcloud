import random

def generate_mac_address():
    # Create a MAC address with the first octet even (unicast & globally unique)
    # by ensuring the second character is one of the even hexadecimal digits.
    mac = [random.choice('02468AEC')] + [random.choice('0123456789ABCDEF') for _ in range(11)]
    
    # Format the MAC address as XX:XX:XX:XX:XX:XX
    mac_address = ':'.join(''.join(mac[i:i+2]) for i in range(0, 12, 2))
    
    return mac_address

# Generate and print a MAC address
print(generate_mac_address())

class IPUtils:
    @staticmethod
    def generate_mac():
        # Create a MAC address with the first octet even (unicast & globally unique)
        # by ensuring the second character is one of the even hexadecimal digits.
        mac = [random.choice('02468AEC')] + [random.choice('0123456789ABCDEF') for _ in range(11)]
        
        # Format the MAC address as XX:XX:XX:XX:XX:XX
        mac_address = ':'.join(''.join(mac[i:i+2]) for i in range(0, 12, 2))
        
        return mac_address
    
    @staticmethod
    def generate_unique_mac(db):
        mac_address = IPUtils.generate_mac()
        while True:
            data = db.interface.find({"mac_address": mac_address})
            if data:
                mac_address = IPUtils.generate_mac()
            else:
                break
        
    
    @staticmethod
    def get_gateway(subnet):
        pass
    
    @staticmethod
    def get_network_mask(subnet):
        pass