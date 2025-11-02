from .iface import Interface

class AppManager(Interface):
    def __init__(self):
        pass

    def send(self, iid: int, package: bytes):
        print(iid, package, 200)

    def modify(self, cmd: str):
        print(f'AppManager modify command: {cmd}')