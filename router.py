import json
import pickle

def check_leek_address(addr):
    for i in addr:
        if not (0 <= i <= 0xFFFF): raise ValueError('Each address component must be between 0 and 65535')
    if len(addr) > 255: raise ValueError('Address length cannot exceed 255 components')
    return True

class RouterException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'RouterException: {self.message}'

class Router:
    def __init__(self):
        self.routetable = {}
        self.replaceaddr = {} # like cname in dns, but for addresses

    def redirect_address(self, addr:tuple[int]):
        check_leek_address(addr)
        if addr not in self.replaceaddr.keys():
            return addr
        return self.replaceaddr[addr]
    
    def add_address_redirect(self, srcs:list[tuple[int]], dst:tuple[int]):
        check_leek_address(dst)
        for src in srcs:
            check_leek_address(src)
            self.replaceaddr[src] = dst

    def remove_address_redirect(self, src:tuple[int]):
        if src in self.replaceaddr.keys():
            del self.replaceaddr[src]

    def modify(self, cmd:str):
        '''
        route add <dst_addr:A[n]> <next_hop:inner_mesh_id[1].node[1]> <length> - add new route
        route del <dst_addr:A[n]> - remove route
        redirect add <src_addr1:A[m],src_addr2:A[k],...> <dst_addr:A[n]> - add address redirections
        redirect del <src_addr:A[m]> - remove address redirection
        '''
        args = cmd.split()
        if args[0] == 'route':
            if args[1] == 'add':
                dst_addr = tuple(map(int, args[2].split('.')))
                next_hop = tuple(map(int, args[3].split('.')))
                length = int(args[4])
                self[dst_addr] = (next_hop, length)
            elif args[1] == 'del':
                dst_addr = tuple(map(int, args[2].split('.')))
                del self[dst_addr]
        if args[0] == 'redirect':
            if args[1] == 'add':
                srcs = [tuple(map(int, addr.split('.'))) for addr in args[2].split(',')]
                dst = tuple(map(int, args[3].split('.')))
                self.add_address_redirect(srcs, dst)
            elif args[1] == 'del':
                src = tuple(map(int, args[2].split('.')))
                self.remove_address_redirect(src)

    def __setitem__(self, k:tuple[int], v:tuple[tuple[int, int], int]):
        '''k is the address of remote node
        v is cortage contain (cortage next_hop(inner_mesh_id, node), int length of path)'''
        if k not in self.routetable.keys():
            self.routetable[k] = v
            return
        if self.routetable[k][1] >= v[1]:
            self.routetable[k] = v

    def __delitem__(self, k:tuple[int]):
        if k in self.routetable.keys():
            del self.routetable[k]
    
    def __getitem__(self, k:tuple[int]):
        redirected_addr = self.redirect_address(k)
        k_parent = redirected_addr
        while k_parent not in self.routetable.keys():
            k_parent = k_parent[:-1]
            if not k_parent: raise RouterException('Router cant route traffic to this node')

        return self.routetable[k_parent][0]
    # TODO: replace pickle
    def save(self):
        with open('router.pkl', 'wb') as f:
            pickle.dump({'route': self.routetable, 'redirects': self.replaceaddr}, f)
    # TODO
    def load(self):
        with open('router.pkl', 'rb') as f:
            data = pickle.load(f)
            self.routetable = data['route']
            self.replaceaddr = data['redirects']
    
if __name__ == '__main__':
    rt = Router()
    #rt.load()
    rt.add_address_redirect([(1234,1), ], (1,))
    rt[(1, )] = (404, 1024*1024)
    print(rt[(1234,1)])
    #rt.save()