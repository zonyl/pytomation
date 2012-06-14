from .common import HAInterface

class UPBInterface(HAInterface):
    def __init__(self, interface=None, *args, **kwargs):
        self.interface = interface
        
