from commands import VM_CRUD_Workflows

vm_name = "ProjectGuestVM"

VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion(vm_name)

