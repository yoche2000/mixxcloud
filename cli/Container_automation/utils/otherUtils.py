import yaml
from Container_automation.southbound_constants import Files

class healthCheckConfiguration:
    @staticmethod
    def createHealthCheckVarsFiles(container_name,target_ips):
        data = {
            "container_name": container_name,
            "target_ips": target_ips
        }
        print(f"Preparing to create the Health Check File: {Files.HEALTHCHECK_VARS_FILE_PATH.value}")
        file_path = f"{Files.HEALTHCHECK_VARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Health Check Configuration File Is Created...")

#healthCheckConfiguration.createHealthCheckVarsFiles("KVPC", "10.2.3.4 10.2.3.6")
class securityConfiguration:
    @staticmethod
    def createRateLimitVarsFiles(container_name, secureLevel):
        # Sample Rule: iptables -A INPUT -p tcp -m state --state NEW -m recent -i KZVPCpubinf --update --seconds 120 --hitcount 2000 -j DROP
        if secureLevel == "HIGH":
            hitcount = 10
        elif secureLevel == "MODERATE":
            hitcount = 100
        elif secureLevel == "LOW":
            hitcount = 200
        else:
            hitcount = 250
        
        rule = [f"iptables -A INPUT -p tcp -m state --state NEW -m recent -i {container_name}pubinf --update --seconds 120 --hitcount {hitcount} -j DROP"]
        #rule = [f"iptables -A INPUT -p TCP -m state --state NEW -i {container_name}pubinf -m recent --update --seconds 60 --hitcount {hitcount} -j DROP"]
        data = {
            "container_name": container_name,
            "rules": rule
        }
        print(f"Preparing to Rate Limit Configuration File: {Files.RATE_LIMIT_FILE_PATH.value}")
        file_path = f"{Files.RATE_LIMIT_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Rate Limit Configuration File Is Created...")
    
    @staticmethod
    def createBlackListVarsFile(container_name, sourceIP):
        # Sample Rule: iptables -A INPUT -i KZVPCpubinf -s 1.1.1.2 -j DROP
        rule = [f"iptables -A INPUT -i {container_name}pubinf -s {sourceIP} -j DROP"]
        data = {
            "container_name": container_name,
            "rules": rule
        }
        print(f"Preparing to Black List IP Configuration File: {Files.BLACKLIST_VARS_FILE_PATH.value}")
        file_path = f"{Files.BLACKLIST_VARS_FILE_PATH.value}"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Black List Configuration File Is Created...")
#securityConfiguration.createRateLimitVarsFiles("KZVPC", "High")
#securityConfiguration.createBlackListVarsFile("KZVPC", "1.1.1.2")