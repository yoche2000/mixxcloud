import yaml

class healthCheckConfiguration:
    @staticmethod
    def createHealthCheckVarsFiles(container_name,target_ips):
        data = {
            "container_name": container_name,
            "target_ips": target_ips
        }
        print(f"Preparing to create the container Configuration File: ../ansible/vars/healthcheck-vars.yml")
        file_path = f"../ansible/vars/healthcheck-vars.yml"
        with open(file_path, 'w') as file:
            yaml.dump(data, file, sort_keys=False)
        print(f"Container Configuration File Is Created...")

#healthCheckConfiguration.createHealthCheckVarsFiles("KVPC", "10.2.3.4 10.2.3.6")
class securityConfiguration:
    @staticmethod
    def createRateLimitVarsFiles(container_name, ):
