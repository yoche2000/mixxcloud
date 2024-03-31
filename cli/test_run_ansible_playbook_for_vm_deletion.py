from commands import VM_CRUD_Workflows

def deletevms(vm_names):
    for each in vm_names:
        VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion(each)

