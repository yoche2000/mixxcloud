class LoadBalancingModel:
    def __init__(self) -> None:
        self.target_group = []
        self.weights = [] 
        self.instance_id = "" # vm instance
        self.interface = "objid" # end_point, vm_interface_name, network_name