from .ha_interface import HAInterface

class Mochad(HAInterface):
    
    def _readInterface(self, lastPacketHash):
        pass
    
    def __getattr__(self, command):
        return lambda address: self._interface.write('pl ' + address + ' ' + command + "\x0D" ) 
