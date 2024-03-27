from enum import Enum

class Files(Enum):
    VMVARS_FILE_PATH = "ansible/vm-vars.yml"
    ROUTERVARS_FILE_PATH = "ansible/router-vars.yml"
    NETWORKVARS_FILE_PATH = "ansible/network-vars.yml"