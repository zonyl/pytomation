import pigpio
from pytomation.interfaces.common import Interface
from pytomation.common.pytomation_object import PytoLogging

class PiGPIOInterface(Interface):
    
    def __init__(self, address, port):
        super(PiGPIOInterface, self).__init__()
        self.hostname = address
        self.port = port
        self._logger = PytoLogging(self.__class__.__name__)
        self.pig = pigpio.pi(self.hostname,self.port)
        self._logger.info("creating pigpiod connection to %s on port %s " % (self.hostname, port))
        
        
    def read(self,address,buffer=1024):
        self._logger.debug("Reading %s " %  (self.pig.read(int(address))))
        return self.pig.read(address)
    
    def write(self, data):
        
        pass
    
    def close(self):
        self._pig.stop()