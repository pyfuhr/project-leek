from zlib import crc32

class y4sm:
    def __init__(self, src_port:int, dst_port:int, data: bytes=b''):
        assert 0<=src_port<=65535, 'src_port must be in 0-65535'; self.src_port = src_port
        assert 0<=dst_port<=65535, 'dst_port must be in 0-65535'; self.dst_port = dst_port
        self.data = data

    def build(self) -> bytes:
        header = bytearray()
        header += self.src_port.to_bytes(2, 'big')
        header += self.dst_port.to_bytes(2, 'big')
        header += len(self.data).to_bytes(2, 'big')
        signature = b'y4sm'
        data = self.data
        package = signature + header + data
        package = package + crc32(package).to_bytes(4, 'big')
        return package

    @staticmethod
    def parse(data:bytes, verify_package=True):
        assert data[:4] == b'y4sm', 'Not y4sm package'
        src_port = int.from_bytes(data[4:6], 'big')
        dst_port = int.from_bytes(data[6:8], 'big')
        data_ln = int.from_bytes(data[8:10], 'big')
        data_ = data[10:10+data_ln]
        package_crc = int.from_bytes(data[10+data_ln:14+data_ln], 'big')

        if verify_package:
            assert package_crc == crc32(data[:-4]), 'Header CRC error'

        return y4sm(src_port, dst_port, data_)
    
    def __or__(self, other):
        if not (isinstance(other, bytes) or isinstance(other, bytearray)):
            other = other.build()
        self.data = other
        return self.build()