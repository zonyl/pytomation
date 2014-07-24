import pigpio
import time
from pytomation.common.pyto_logging import PytoLogging
from pytomation.common.pytomation_api import PytomationAPI
from .ha_interface import HAInterface
from .common import *
from pytomation.devices.state import State
class RemotePi(HAInterface):
    
    def __init__(self, interface, sensorPairs = None, *args, **kwargs):
        self._logger = PytoLogging(self.__class__.__name__)
        self._logger.info("doing __init__")
        super(RemotePi, self).__init__(interface, *args, **kwargs)
        #self.hostname = interface[0]
        #self.port = interface[1]   
        self.gpioPi = interface
        self.sensorPairs = sensorPairs
        #print ("Got hostname %s and port %s"% (self.hostname,self.port))
        
    def _init(self,*args, **kwargs):
        self._logger.info("doing _init")
        super(RemotePi, self)._init(*args, **kwargs)
        self._logger.info("devices %s" % (self._devices))
    def _processInterrupt(self,gpioID, value, tick):
        self._logger.info("Got %s from %s" % (value, gpioID))
       # paired = [pin for pin in pair for pair in self.sensorPairs if gpioID in pair]
        #if gpioID in self.sensorPairs:
        #   if value | self.gpioPi.read(self.sensorPairs[gpioID]):
        #        self._onCommand(Command.MOTION,gpioID)
        values = [value,]
        myAddress = gpioID
        myState = State.UNKNOWN
        paired = [pair for pair in self.sensorPairs if gpioID in pair]
        if paired:
            for p in paired[0]:
                if p != gpioID:
                    
                    values.append(self.gpioPi.read(p))
                    print self.gpioPi.read(p)        

        for device in self._devices:
            #print device
            #print device.state
            if paired:
                if device.addressMatches(paired[0][0]):
                    myState = device.state
                    myAddress = paired[0][0]

            else:
                if device.addressMatches(gpioID):
                    myState = device.state

        

        print ("My state is equal to still %s" % (myState==State.STILL))
        if any(values) & (myState != State.MOTION):
            #print "sending motion"
            self._onCommand(Command.MOTION  ,myAddress)
        if (not any(values)) & (myState != State.STILL):
            #print "sending still %s" % (myState!=State.STILL)
            self._onCommand(Command.STILL,myAddress)
    
    def _readInterface(self,lastPacketHash):
        pass
        #self._logger.info("read interface lastPacketHash %s " % (lastPacketHash))

    def onCommand(self,callback=None, address=None, device=None):
        self._logger.info("registering GPIO %s on device %s" % (device.address,device))
        
       
        self._logger.info("my interface %s  %s" % (self._interface,self.gpioPi) )

        paired = [pair for pair in self.sensorPairs if device.address in pair]

        if paired:
            self._logger.info("Got a pair %s  %s" % (device.address, paired) )
            for p in paired[0]:
                self.gpioPi.pig.set_mode(p,pigpio.INPUT)
                self.gpioPi.pig.callback(p,pigpio.EITHER_EDGE, self._processInterrupt)
        else:
            self.gpioPi.pig.set_mode(device.address,pigpio.INPUT)
            self.gpioPi.pig.callback(device.address,pigpio.EITHER_EDGE, self._processInterrupt)
        self._logger.info("registering GPIO %s" % (address))
        if not device:
            self._logger.info("GOT HERE")
            self._commandDelegates.append({
                                       'address': address,
                                       'callback': callback,
                                       })
        else:
            self._devices.append(device)

        
        