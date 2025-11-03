from .iface import Interface
from protocols import y3ip, y4sm

def extract_data(package:bytes|bytearray):
    match package[:4]:
        case b'y3ip':
            print('> Unpack y3ip package')
            pkg = y3ip.parse(package)
            print(f'\t>> From address {pkg.src_addr} to {pkg.dst_addr}')
            return extract_data(pkg.data)
        case b'y4sm':
            print('> Unpack y4sm package')
            pkg = y4sm.parse(package)
            print(f'\t>> From port {pkg.src_port} to {pkg.dst_port}')
            return extract_data(pkg.data)
        case _:
            print('> Reached data or unknown protocol')
            return package


class AppManager(Interface):
    def __init__(self):
        pass

    def send(self, iid: int, package: bytes):
        print(extract_data(package))

    def modify(self, cmd: str):
        print(f'AppManager modify command: {cmd}')