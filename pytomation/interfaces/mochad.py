from .ha_interface import HAInterface
import time

class Mochad(HAInterface):
    
#    def _readInterface(self, lastPacketHash):
#        pass

    def _readInterface(self, lastPacketHash):
       time.sleep(0.5)

    def status(self):
       self._interface.write('st'+"\x0D")
       return self._interface.read()

    def _onCommand(self, command=None, address=None):
        commands = command.split(' ')
        if commands[0] == 'pl':
            address = commands[1]
            command = commands[2][0:len(commands[2])-1]
        super(Mochad, self)._onCommand(command=command, address=address)
    
    def __getattr__(self, command):
        return lambda address: self._interface.write('rf ' + address + ' ' + command + "\x0D" ) 
