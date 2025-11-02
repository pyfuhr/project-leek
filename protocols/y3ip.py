from zlib import crc32
import logging
from .utils import unpackaddr, packaddr, unpackflags, packflag

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Y3IPException(Exception):
    def __init__(self, message:str):
        self.message = message

    def __str__(self):
        return f'Y3IPException: {self.message}'

class Y3IP:
    def __init__(self, version:int, hop_param:list[bool], fragment_offset:int, ttl:int, nt:int, src_addr:tuple[int], dst_addr:tuple[int], inner_package:bytes, data: bytes):
        assert 0<=version<=255, 'Version must be in 0-255'; self.version = version
        self.hop_param = hop_param
        assert 0<=fragment_offset<=65535, 'Offset must be in 0-65535'; self.fragment_offset = fragment_offset
        assert 0<=ttl<=255, 'TTL must be in 0-255'; self.ttl = ttl
        assert 0<=nt<=255, 'NT must be in 0-255'; self.nt = nt
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        assert 0<=inner_package<=255, 'package id must be in 0-255'; self.inner_package = inner_package
        self.data = data

    def build(self) -> bytes:
        header = bytearray()
        header += packflag(self.hop_param) # hop param, header start here
        header += self.fragment_offset.to_bytes(2, 'big') #
        header += bytes((self.ttl, ))
        header += bytes((self.nt, ))
        header += packaddr(self.src_addr)
        header += packaddr(self.dst_addr)
        header += bytes((self.inner_package, ))
        header += len(self.data).to_bytes(2, 'big')
        header_crc = crc32(header).to_bytes(4, 'big')
        header_ln = len(header).to_bytes(2, 'big')
        signature = b'y3ip'
        version = bytes((self.version, ))
        data = self.data
        package = signature + version + header_ln + header + header_crc + data
        package = package + crc32(package).to_bytes(4, 'big')
        return package

    @staticmethod
    def parse(data:bytes, verify=True, verify_header=False):
        assert data[:4] == b'y3ip', 'Not y3ip package'
        version = data[4]
        header_ln = int.from_bytes(data[5:7], 'big')
        hop_param = unpackflags(bytes((data[7], )))
        fragment_off = int.from_bytes(data[8:10], 'big')
        ttl = data[10]
        nt = data[11]
        src_ln = data[12]
        dst_ln = data[12+src_ln*2+1]
        src_addr = unpackaddr(data[12:12+src_ln*2+1])
        dst_addr = unpackaddr(data[12+src_ln*2+1:12+src_ln*2+1+dst_ln*2+1])
        addr_offset = 12+src_ln*2+1+dst_ln*2+1
        inner_package = data[addr_offset]
        data_ln = int.from_bytes(data[addr_offset+1:addr_offset+3], 'big')
        header_crc = int.from_bytes(data[addr_offset+3:addr_offset+7], 'big')
        data_ = data[addr_offset+7:addr_offset+7+data_ln]
        package_crc = int.from_bytes(data[addr_offset+7+data_ln:addr_offset+7+data_ln+4], 'big')

        if verify_header:
            header = data[7:addr_offset+3]
            assert header_crc == crc32(header), 'Header CRC error'
        if verify:
            assert package_crc == crc32(data[:-4]), "Package CRC error"

        return Y3IP(version, hop_param, fragment_off, ttl, nt, src_addr, dst_addr, inner_package, data)

    @staticmethod
    def get_addr(data:bytes) -> list[tuple[int]]:
        '''returns src_addr: tuple[int], dst_addr: tuple[int]'''
        src_ln = data[12]
        dst_ln = data[12+src_ln*2+1]
        src_addr = unpackaddr(data[12:12+src_ln*2+1])
        dst_addr = unpackaddr(data[12+src_ln*2+1:12+src_ln*2+1+dst_ln*2+1])
        return src_addr, dst_addr
    
    @staticmethod
    def decrease_ttl(data:bytes) -> bytes:
        data = bytearray(data)
        if data[10] == 0:
            raise Y3IPException('TTL expired')
        data[10] -= 1
        return data
    
    @staticmethod
    def decrease_nt(data:bytes) -> bytes:
        data = bytearray(data)
        if data[11] == 0:
            raise Y3IPException('NT expired')
        data[11] -= 1
        return data