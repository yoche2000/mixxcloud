from commands import VM_CRUD_Workflows

vm_name = ["RVM_B_B-B", "RVM_C_C-C"]

for each in vm_name:
    VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion(each)

