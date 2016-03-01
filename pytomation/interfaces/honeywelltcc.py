import time
from pyhwtherm import PyHWTherm
from .ha_interface import HAInterface
from pytomation.devices import State,Command

class HoneywellTCC(HAInterface):
    VERSION = '0.0.1'

    FANAUTO = 0
    FANON = 1

    SYSTEMOFF = 2
    SYSTEMHEAT = 1
    SYSTEMCOOL = 3
    SYSTEMAUTO = 4

    def __init__(self, username, password, deviceid, *args, **kwargs):
	self._pyhwtherm = PyHWTherm(username=username, password=password, deviceid=deviceid)
	self._poll_secs = kwargs.get('poll', 7200)
	if self._poll_secs < 3600:
		self._poll_secs = 3600
	self._iteration = self._poll_secs
	self._deviceid = deviceid
	super(HoneywellTCC, self).__init__(None, *args, **kwargs)

    def _init(self, *args, **kwargs):
	super(HoneywellTCC, self)._init(*args, **kwargs)
	self._last_temp = None
	self._mode = None
	self._hold = None
	self._fan = None
	self._set_point = None
	self._away = None


    def _readInterface(self, lastPacketHash):
	if not self._iteration < self._poll_secs:
	    self._iteration = 0
	    print "checking ..."
	    print self.status()

	else:
	    self._iteration+=1
	    time.sleep(1)

    def _send_state(self):
	 try:
	     self._pyhwtherm.login()
	     self._pyhwtherm.submit()
	     self.devicedata = self._pyhwtherm.query()
	     self._pyhwtherm.logout()
	 except Exception, ex:
             #self._logger.error('Could not formulate command to send: ' + str(ex))
             print 'Could not formulate command to send: ' + str(ex)


    def circulate(self, *args, **kwargs):
	 self._pyhwtherm.fan("on")
	 self._fan = True
	 return self._send_state()

    def still(self, *args, **kwargs):
	 self._pyhwtherm.fan("auto")
	 self._fan = False
	 return self._send_state()

    def status(self, *args, **kwargs):
	    print "STATUS CALLED!"
	    self._pyhwtherm.login()
	    self.devicedata = self._pyhwtherm.query()
	    print self.devicedata
	    self._pyhwtherm.logout()
	    temp = self.devicedata['latestData']['uiData']['DispTemperature']
	    self._mode = self.devicedata['latestData']['uiData']['SystemSwitchPosition']
            #import pdb; pdb.set_trace()
	    self._heatSetPoint = self.devicedata['latestData']['uiData']['HeatSetpoint']
	    self._coolSetPoint = self.devicedata['latestData']['uiData']['CoolSetpoint']

	    self._hold = None
	    #self._fan = self.devicedata['latestData']['fanData']['fanMode']
	    self._away = None

	    if temp != self._last_temp:
		    print "Setting temp", temp, self._last_temp
		    self._last_temp = temp
	            self._onCommand(command=(Command.LEVEL,self._last_temp) ,address=self._deviceid)


	    if self.devicedata['latestData']['fanData']['fanMode'] == self.FANAUTO:
		    print "fanmode Auto"
		    self._fan = False
		    self._onCommand(command=Command.STILL, address=self._deviceid)
	    else:
		    print "fanmode ON"
		    self._fan = True
		    self._onCommand(command=Command.CIRCULATE, address=self._deviceid)


            #import pdb; pdb.set_trace()
	    if self._mode == self.SYSTEMAUTO or self._mode == 5:
		    self._onCommand(command=Command.AUTOMATIC, address=self._deviceid)
		    
		    if (self._coolSetPoint - temp) < (temp - self._heatSetPoint):
			    # If closer to cool update show cool setpoint
			    self._onCommand(command=(Command.SETPOINT, self._coolSetPoint), address=self._deviceid)
		    else:
			    #
			    self._onCommand(command=(Command.SETPOINT, self._heatSetPoint), address=self._deviceid)

	    if self._mode == self.SYSTEMHEAT:
		    self._onCommand(command=Command.HEAT, address=self._deviceid)
		    self._onCommand(command=(Command.SETPOINT, self._heatSetPoint), address=self._deviceid)
	    if self._mode == self.SYSTEMCOOL:
		    self._onCommand(command=Command.COOL, address=self._deviceid)
		    self._onCommand(command=(Command.SETPOINT, self._coolSetPoint), address=self._deviceid)
	    if self._mode == self.SYSTEMOFF:
		    self._onCommand(command=Command.OFF, address=self._deviceid)

    def vacate(self, *args, **kwargs):
	    self._pyhwtherm.cancelHold()
	    return self._send_state()

    def heat(self, *args, **kwargs):
	    self._pyhwtherm.systemState('heat')
	    return self._send_state()

    def cool(self, *args, **kwargs):
	    self._pyhwtherm.systemState('cool')
	    return self._send_state()

    def off(self, *args, **kwargs):
	    self._pyhwtherm.systemState('off')
	    return self._send_state()

    def setpoint(self, address, level, timeout=2.0):
	    #
	    if self._mode == self.SYSTEMAUTO or self._mode == 5:
		    self._onCommand(command=Command.AUTOMATIC, address=self._deviceid)
		    
		    if (self._coolSetPoint - temp) < (temp - self._heatSetPoint):
			    # If closer to cool update show cool setpoint
			    self._onCommand(command=(Command.SETPOINT, self._coolSetPoint), address=self._deviceid)
			    self._pyhwtherm.permHold(cool=level)
		    else:
			    #
			    self._onCommand(command=(Command.SETPOINT, self._heatSetPoint), address=self._deviceid)
			    self._pyhwtherm.permHold(heat=level)

	    if self._mode == self.SYSTEMHEAT:
		    self._onCommand(command=Command.HEAT, address=self._deviceid)
		    self._onCommand(command=(Command.SETPOINT, self._heatSetPoint), address=self._deviceid)
		    self._pyhwtherm.permHold(heat=level)
	    if self._mode == self.SYSTEMCOOL:
		    self._onCommand(command=Command.COOL, address=self._deviceid)
		    self._onCommand(command=(Command.SETPOINT, self._coolSetPoint), address=self._deviceid)
		    self._pyhwtherm.permHold(cool=level)

	    return self._send_stat()

	



