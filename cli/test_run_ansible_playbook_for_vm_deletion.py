from commands import VM_CRUD_Workflows

vm_name = ["RouterVM-Copy", "RVM_DELTA_NEWVPC", "RouterVM1" ]

for each in vm_name:
    VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion(each)

