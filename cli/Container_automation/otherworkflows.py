from southbound_constants import Files
import yaml

class healthCheckWorkflow:
    @staticmethod
    def startHealthCheck(container_name,target_ips):
        """
        @params:
        - container_name: Name of the Iaas LB Container or LBaaS Container
        - target_ips: Space Separated Target IPs to Monitor the Health
        Sample:
        # ip netns exec KVPC python3 healthcheck.py 10.2.3.4 10.2.3.6
        """
        command = ["ansible-playbook", "-i", "ansible/inventory/hosts.ini", "Container_automation/ansible/start_healthcheck.yml", '-l', 'even']
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Container Configuration File Is Created...")

   