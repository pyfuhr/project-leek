class Interface:
    def __init__(self):
        raise NotImplementedError()
    def send(self, iid: int, package:bytes):
        raise NotImplementedError()
    def modify(self, cmd:str):
        # in cmd you should add info about inner_mesh_id (for calculate nt)
        raise NotImplementedError()