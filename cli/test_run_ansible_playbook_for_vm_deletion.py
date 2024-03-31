from commands import VM_CRUD_Workflows

vm_name = ["RVM_DELTA1_HOLIVPC", "RVM_DELTA2_HOLIVPC", "RVM_DELTA2_HOLIVPC2" ]

for each in vm_name:
    VM_CRUD_Workflows.run_ansible_playbook_for_vm_deletion(each)

