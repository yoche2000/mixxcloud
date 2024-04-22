from enum import Enum

class Files(Enum):
    VMVARS_FILE_PATH = "ansible/vm-vars.yml"
    ROUTERVARS_FILE_PATH = "ansible/router-vars.yml"
    NETWORKVARS_FILE_PATH = "ansible/network-vars.yml"
    CONTAINER_VARS_FILE_PATH = "Container_automation/ansible/vars/container-vars.yml"
    HEALTHCHECK_VARS_FILE_PATH = "Container_automation/ansible/vars/healthcheck-vars.yml"
    VETH_VARS_FILE_PATH = "Container_automation/ansible/vars/veth-vars.yml"
    SUBNET_VARS_FILE_PATH = "Container_automation/ansible/vars/subnet-vars.yml"
    VM_VARS_FILE_PATH = "Container_automation/ansible/vars/vm-vars.yml"
    LB_VARS_FILE_PATH = "Container_automation/ansible/vars/lb-vars.yml"
    BLACKLIST_VARS_FILE_PATH = "Container_automation/ansible/vars/fw-blacklist-vars.yml"
    RATE_LIMIT_FILE_PATH = "Container_automation/ansible/vars/fw-ratelimit-vars.yml"