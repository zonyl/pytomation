from .common import *
from .ha_interface import HAInterface
#from pytomation.devices import State

class Mochad(HAInterface):
    
    VERSION='0.2'

    def _readInterface(self, lastPacketHash):
        """
	01/27 23:41:23 Rx RF HouseUnit: A3 Func: Off
	0     1        2  3  4          5  6     7 
	01/27 23:48:23 Rx RF HouseUnit: A1 Func: On
	12/07 20:49:37 Rx RFSEC Addr: C6:1B:00 Func: Motion_alert_MS10A
	0     1        2  3     4     5        6     7
	"""
        responses = self._interface.read()
	if len(responses) >=4:
	    self._logger.debug('responses> ' + responses)
	    data=responses.split(' ')
	    #ate=data[0]
	    #ime=data[1]
	    direction=data[2]
	    method=data[3]
	    #ua=data[4]
	    addr=data[5]
	    #func junk
	    func=data[7].strip()
	    #self._onCommand(command=func.upper(),address=address)

	    if func=="On":
	        print "on"
	        self.on(address=addr)
	    elif func=="Off":
	        self.off(address=addr)
	    elif func=="Motion_alert_MS10A":
	        self._onCommand(command=Command.MOTION,address=addr)
	    elif func=="Motion_normal_MS10A":
	        self._onCommand(command=Command.STILL,address=addr)

	    

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
        self._logger.debug('[Mochad] Command on at '+address)
	self._onCommand(command=Command.ON,address=address)
        self._interface.write('rf ' + address + ' on' + "\x0D")

    def off(self, address):
        self._logger.debug('[Mochad] Command off at '+address)
	self._onCommand(command=Command.OFF,address=address)
        self._interface.write('rf ' + address + ' off'+ "\x0D")

    def version(self):
        self._logger.info("Mochad Pytomation Driver version " + self.VERSION)

