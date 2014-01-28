from .ha_interface import HAInterface
#from pytomation.devices import State

class Mochad(HAInterface):
    
    VERSION='0.2'

#    def _readInterface(self, lastPacketHash):
#        pass     

    def rawstatus(self):
        self._interface.write('st'+"\x0D")
        return self._interface.read()

    def status(self,address):
        """
        print "Status of Address: " + str(address)
        self._interface.write('st'+"\x0D")
        data=self._interface.read()
        
        if len(address)==2:   #normal housecode address
	   print address[0].upper()
	   return State.ON

        if len(address)==6:   #sensor address
           return State.ON
	    """
        self._logger.debug('Mochad Status called')
        return  
    
    def update_status(self):
        self._logger.debug('Mochad update status called')
        for d in self._devices:
            self._logger.debug('... '+ d.address)
            self.status(d.address)

    def _onCommand(self, command=None, address=None):
        commands = command.split(' ')
        if commands[0] == 'rf':
            address = commands[1]
            command = commands[2][0:len(commands[2])-1]
        self._logger.debug('[Mochad] Command>'+command+' at '+address)
        super(Mochad, self)._onCommand(command=command, address=address)
    
    """ 
    def __getattr__(self, command):
        return lambda address: self._interface.write('rf ' + address + ' ' + command + "\x0D" ) 
    """

    def on(self, address):
        self._interface.write('rf ' + address + ' on' + "\x0D")

    def off(self, address):
        self._interface.write('rf ' + address + ' off'+ "\x0D")

    def version(self):
        self._logger.info("Mochad Pytomation Driver version " + self.VERSION)

