from commands import VM_CRUD_Workflows

def control_stmt(func, success, failure):
    if func and func():
        success and success()
    else:
        failure and failure()

class VMController:
    @staticmethod
    def create(vm_name, vCPU, memory, disk_size, interfaces, success = None, failure = None):
        if VM_CRUD_Workflows.run_ansible_playbook_for_vm_definition(vm_name, vCPU, memory, disk_size, interfaces):
            success and success()
        else:
            failure and failure()
    
    @staticmethod
    def destroy(vm_name, success = None, failure = None):
        if VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion(vm_name):
            success and success()
        else:
            failure and failure()
    
    @staticmethod
    def start(vm_name, success = None, failure = None):
        if VM_CRUD_Workflows.run_ansible_playbook_for_vm_start(vm_name):
            success and success()
        else:
            failure and failure()
    
    @staticmethod
    def shutdown():
        pass
    
    @staticmethod
    def pause():
        pass
    
    @staticmethod
    def resume():
        pass
    
    # @staticmethod
    # def 