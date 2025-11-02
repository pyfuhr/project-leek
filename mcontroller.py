import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from router import Router
from iface import Interface, AppManager
from protocols import Y3IP

def parse_y3ip(data:bytes):
    '''returns
    dst_addr: tuple[int]
    src_addr: tuple[int]
    mode: int (0-min delay, 1-max_bandwidth, 2-max_safety)
    ttl: int
    nt: int
    inner_package: int
    data: bytearray
    '''
    raise NotImplementedError()

def extract_y3ip_dst_addr(data:bytes)->tuple[int]:
    '''returns dst_addr: tuple[int]'''
    raise NotImplementedError()

def decrease_ttl(data:bytes)->bytes:
    return data
    # send_y3cm(self.meta["local_address"][0], dst_addr, 'ttl expired') # TTL expired
    raise NotImplementedError()

def decrease_nt(data:bytes)->bytes:
    raise NotImplementedError()

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
        dst_addr = Y3IP.get_addr(package)[1]          
        if dst_addr in self.meta.get("local_address", []):
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
            package = decrease_nt(package) # if next_hop inner_mesh_id != inner_mesh_id of package you should decrease nt
        package = Y3IP.decrease_ttl(package)
        
        if next_hop not in self.commutator.keys():
            raise ValueError('No such interface to send packet')
        interface_id, iid = self.commutator[next_hop]
        self.interfaces[interface_id].send(iid, package)

if __name__ == '__main__':
    mc = MController()
    mc.add_interface(0, AppManager())
    mc.router.modify('route add 1234.1 0.0 200')
    mc.add_node((0, 0), 0, 0)
    pkg = Y3IP(0, [0, 0, 0, 0, 0, 0, 0, 0], 0, 50, 3, (11,11,11), (1234, 1), 0, b'Hello, world!').build()
    mc.process_packet(bytes((0, )) + pkg)