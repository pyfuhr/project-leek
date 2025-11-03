from zlib import crc32
import logging
from .utils import unpackaddr, packaddr, unpackflags, packflag

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class y3ipException(Exception):
    def __init__(self, type:int, message:str):
        self.type = type
        self.message = message

    def __str__(self):
        return f'Y3IPException: Err{self.type}:{self.message}'

class y3ip:
    def __init__(self, version:int, id:int, hop_param:list[bool], fragment_offset:int, ttl:int, nt:int, src_addr:tuple[int], dst_addr:tuple[int], data: bytes=b''):
        assert 0<=version<=255, 'Version must be in 0-255'; self.version = version
        assert 0<=id<=4294967295, 'id must be in 0-4294967295'; self.id = id
        self.hop_param = hop_param
        assert 0<=fragment_offset<=65535, 'Offset must be in 0-65535'; self.fragment_offset = fragment_offset
        assert 0<=ttl<=255, 'TTL must be in 0-255'; self.ttl = ttl
        assert 0<=nt<=255, 'NT must be in 0-255'; self.nt = nt
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.data = data

    def build(self) -> bytes:
        header = bytearray()
        header += self.id.to_bytes(4, 'big')
        header += packflag(self.hop_param) # hop param, header start here
        header += self.fragment_offset.to_bytes(2, 'big') #
        header += self.ttl.to_bytes(2, 'big')
        header += bytes((self.nt, ))
        header += packaddr(self.src_addr)
        header += packaddr(self.dst_addr)
        header += len(self.data).to_bytes(2, 'big')
        header_crc = crc32(header).to_bytes(4, 'big')
        header_ln = len(header).to_bytes(2, 'big')
        signature = b'y3ip'
        version = bytes((self.version, ))
        data = self.data
        package = signature + version + header_ln + header + header_crc + data
        package = package + crc32(data).to_bytes(4, 'big')
        return package

    @staticmethod
    def parse(data:bytes, verify_header=True, verify_data=False):
        assert data[:4] == b'y3ip', 'Not y3ip package'
        version = data[4]
        header_ln = int.from_bytes(data[5:7], 'big')
        id = int.from_bytes(data[7:11], 'big')
        hop_param = unpackflags(bytes((data[11], )))
        fragment_off = int.from_bytes(data[12:14], 'big')
        ttl = int.from_bytes(data[14:16], 'big')
        nt = data[16]
        src_ln = data[17]
        dst_ln = data[17+src_ln*2+1]
        src_addr = unpackaddr(data[17:17+src_ln*2+1])
        dst_addr = unpackaddr(data[17+src_ln*2+1:17+src_ln*2+1+dst_ln*2+1])
        addr_offset = 17+src_ln*2+1+dst_ln*2+1
        data_ln = int.from_bytes(data[addr_offset:addr_offset+2], 'big')
        header_crc = int.from_bytes(data[addr_offset+2:addr_offset+6], 'big')
        data_ = data[addr_offset+6:addr_offset+6+data_ln]
        package_crc = int.from_bytes(data[addr_offset+6+data_ln:addr_offset+6+data_ln+4], 'big')

        if verify_header:
            header = data[7:addr_offset+2]
            assert header_crc == crc32(header), 'Header CRC error'
        if verify_data:
            assert package_crc == crc32(data_), "Data CRC error"

        return y3ip(version, id, hop_param, fragment_off, ttl, nt, src_addr, dst_addr, data_)

    @staticmethod
    def get_addr(data:bytes) -> list[tuple[int]]:
        '''returns src_addr: tuple[int], dst_addr: tuple[int]'''
        src_ln = data[17]
        dst_ln = data[17+src_ln*2+1]
        src_addr = unpackaddr(data[17:17+src_ln*2+1])
        dst_addr = unpackaddr(data[17+src_ln*2+1:17+src_ln*2+1+dst_ln*2+1])
        return src_addr, dst_addr
    
    @staticmethod
    def update_header_crc32(data:bytes) -> bytes:
        data = bytearray(data)
        header_ln = int.from_bytes(data[5:7])
        header = data[7:7+header_ln]
        header_crc = crc32(header)
        data[7+header_ln:7+header_ln+4] = header_crc.to_bytes(4, 'big')
        return data

    @staticmethod
    def decrease_ttl(data:bytes) -> bytes:
        data = bytearray(data)
        ttl = int.from_bytes(data[14:16], 'big')
        if ttl == 0:
            raise y3ipException(0, 'TTL expired')
        ttl -= 1
        data[14:16] = ttl.to_bytes(2, 'big')
        pass
        data = y3ip.update_header_crc32(data)
        return data
    
    @staticmethod
    def decrease_nt(data:bytes) -> bytes:
        data = bytearray(data)
        if data[16] == 0:
            raise y3ipException(1, 'NT expired')
        data[16] -= 1
        data = y3ip.update_header_crc32(data)
        return data
    
    def __or__(self, other):
        if not (isinstance(other, bytes) or isinstance(other, bytearray)):
            other = other.build()
        self.data = other
        return self.build()
    

    
if __name__ == "__main__":
    pack = y3ip(1, 435345434, [0,0,0,0,0,0,0,0], 0, 40, 5, [10, 20], [30, 40], b'Hello world')
    bytepack = pack.build()

    pack2 = y3ip.parse(bytepack)
    print(pack2.version)
    print(pack2.id)
    print(pack2.hop_param)
    print(pack2.fragment_offset)
    print(pack2.ttl)
    print(pack2.nt)
    print(pack2.src_addr)
    print(pack2.dst_addr)
    print(pack2.data)