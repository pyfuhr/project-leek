import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from router import Router
from iface import Interface, AppManager
from protocols import y3ip, y4sm

class MController:
    def __init__(self):
        self.interfaces = {}
        self.commutator: dict[tuple(int, int): tuple(int, int)] = {} # next_hop(inner_mesh_id, node): (interface_id, iid)
        self.router = Router()
        self.meta = {}
        # meta["local_address"] = list[tuple[int]] - list of my addresses, package will route to
        # applications manager (self.interfaces[0]) and then to listening application

    def add_interface(self, id:int, interface:Interface):
        # pid is 
        self.interfaces[id] = interface
        logger.info(f'Interface added with id:{id}')

    def modify_interface(self, id:int, cmd:str):
        if id not in self.interfaces.keys():
            raise ValueError('No such interface')
        self.interfaces[id].modify(cmd)
    
    def del_interface(self, id:int):
        if id in self.interfaces.keys():
            del self.interfaces[id]
            logger.info(f'Interface with id:{id} deleted')
        else:
            logger.warning('No such interface to delete')

    def add_node(self, addr:tuple[int, int], interface_id:int, iid:int=0):
        self.commutator[addr] = (interface_id, iid)

    def remove_node(self, interface_id:int):
        if interface_id in self.commutator.keys():
            del self.commutator[interface_id]
        else:
            logger.warning('No such node to remove')

    def route_packet(self, package:tuple[int]): 
        dst_addr = y3ip.get_addr(package)[1]          
        if dst_addr in self.meta.get("local_addresses", []):
            next_hop = (0, 0) # interface 0 is application manager
        else:
            next_hop = self.router[dst_addr]
        return next_hop
    
    def process_packet(self, bpackage:bytes): 
        inner_mesh_id = bpackage[0]
        package = bpackage[1:]
        # iface add 1 byte in the beginning of package to identify inner_mesh_id
        next_hop = self.route_packet(package)
        if next_hop[0] != inner_mesh_id:
            package = y3ip.decrease_nt(package) # if next_hop inner_mesh_id != inner_mesh_id of package you should decrease nt
        package = y3ip.decrease_ttl(package)
        if next_hop not in self.commutator.keys():
            raise ValueError('No such interface to send packet')
        interface_id, iid = self.commutator[next_hop]
        self.interfaces[interface_id].send(iid, package)

if __name__ == '__main__':
    mc = MController()
    mc.add_interface(0, AppManager())
    mc.router.modify('route add 1234.1.33 1.2 200')
    mc.router.modify('route add 12.2.2 0.0 0')
    mc.add_node((0, 0), 0, 0)
    pkg = y3ip(0, 333, [0, 0, 0, 0, 0, 0, 0, 0], 0, 50, 3, (11,11,11), (12,2,2)) | y4sm(10244, 1024, b'Hello world')
    mc.process_packet(bytes((0, )) + pkg)