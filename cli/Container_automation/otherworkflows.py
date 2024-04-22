from Container_automation.utils.otherUtils import healthCheckConfiguration, securityConfiguration
import yaml
import subprocess
import json
from southbound_utils import Commands

class healthCheckWorkflow:
    @staticmethod
    def run_ansible_playbook_to_start_healthcheck(container_name, target_ips, region):
        """
        @params:
        - container_name: Name of the Iaas LB Container or LBaaS Container
        - target_ips: Space Separated String Target IPs to Monitor the Health
        Sample:
        # ip netns exec KVPC python3 healthcheck.py 10.2.3.4 10.2.3.6
        """
        # TODO: target_ips needs to be converted into space separated string.
        try:
            print(f"Health Check on {container_name} has been triggered..")
            healthCheckConfiguration.createHealthCheckVarsFiles(container_name, target_ips)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "ansible/start_healthcheck.yml"]
            if region is not None:
                command.extend(['-l', region])
            Commands.run_command(command)
        except Exception as error:
            print(f"Failure in Health Check Creation. More details: {error}")
            return False

class securityWorkflow:
    @staticmethod
    def run_ansible_playbook_to_apply_blacklist_rules(container_name, sourceIP, region):
        try:
            print(f"Black List on {container_name} for Source IP: {sourceIP} has been triggered..")
            securityConfiguration.createBlackListVarsFile(container_name, sourceIP)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "ansible/create_rules_fw_blacklist.yml"]
            if region is not None:
                command.extend(['-l', region])
            Commands.run_command(command)
        except Exception as error:
            print(f"Failure in Applying Black List Rules. More details: {error}")
            return False
    
    @staticmethod
    def run_ansible_playbook_to_apply_ratelimit_rules(container_name, secureLevel, region):
        "secureLevel can take: HIGH, MODERATE, LOW"
        try:
            print(f"Ratelimit on {container_name} for Secure: {secureLevel} has been triggered..")
            securityConfiguration.createRateLimitVarsFiles(container_name, secureLevel)
            command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "ansible/create_rules_fw_ratelimit.yml"]
            if region is not None:
                command.extend(['-l', region])
            Commands.run_command(command)
        except Exception as error:
            print(f"Failure in Rate Limit Rules. More details: {error}")
            return False


# healthCheckWorkflow.run_ansible_playbook_to_start_healthcheck("LBCG", "192.168.42.3 192.168.42.4", "even")
# securityWorkflow.run_ansible_playbook_to_apply_blacklist_rules("LBCG","1.1.1.1","odd")
#securityWorkflow.run_ansible_playbook_to_apply_ratelimit_rules("LBCG", "HIGH","even")