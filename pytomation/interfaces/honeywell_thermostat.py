"""
Honeywell Thermostat Pytomation Interface

Author(s):
texnofobix@gmail.com

Idea/original code from:
Brad Goodman http://www.bradgoodman.com/  brad@bradgoodman.com

some code ideas from:
 George Farris <farrisg@gmsys.com>

Switched to use Python Requests
"""
import requests
import datetime
import time

from .ha_interface import HAInterface
from .common import Interface, Command
from pytomation.devices import State


class HoneywellWebsite(Interface):
    VERSION = '2.0.0'

    _headers={
    	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0',
	'Host': 'rs.alarmnet.com',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-US,en;q=0.5',
	'Referer': 'https://rs.alarmnet.com/TotalConnectComfort'
	}

    def __init__(self, username=None, password=None):
        super(HoneywellWebsite, self).__init__()

        self._host = "rs.alarmnet.com"
        self._username = username
        self._password = password
        self._loggedin = False
	self._session = None
        self._logger.debug('Created object for user> ' + str(username))
        try:
            self._login()
        except Exception, ex:
            self._logger.debug('Error logging in> ' + str(username)
                               + 'exception: ' + str(ex))

    def _login(self):
        self._session = requests.Session()
	params = {
		'timeOffset':240,
		'UserName':self._username,
		'Password':self._password,
		'RememberMe':'false'
		}

	login_request=self._session.post(
	    'https://rs.alarmnet.com/TotalConnectComfort',
	    params=params,
	    headers=self._headers
	    )

        if login_request.status_code != 200:
            self._logger.warning('Failed HTTP Code> ' + str(login_request.status_code))
            self._loggedin = False
        else:
            self._logger.debug('Login passed. HTTP Code> ' + str(login_request.status_code))
            self._loggedin = True
	
    def _query(self, address):
	    #if (self._loggedin):
	    #    verifylogin_request=self._session.get(
	    #        'https://rs.alarmnet.com/TotalConnectComfort/Device/Control/'+str(address),
		#    headers=self._headers)

	    #if verifylogin_request.status_code != 200:
	    #    self._loggedin = False
            self._logger.debug('Querying Thermostat>'+str(address))
            t = datetime.datetime.now()
            utc_seconds = (time.mktime(t.timetuple()))
            utc_seconds = int(utc_seconds * 1000)

	    self._control_headers = {
	        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0',
		'Host': 'rs.alarmnet.com',
		"Referer":"https://rs.alarmnet.com/TotalConnectComfort/Device/Control/"+str(address),
		"X-Requested-With":"XMLHttpRequest",
		'Accept': '*/*',
		'Accept-Language': 'en-US,en;q=0.5',
		}


	    query_request=self._session.get(
	        'https://rs.alarmnet.com/TotalConnectComfort/Device/CheckDataSession/'+
	        str(address)+'?_='+
		str(utc_seconds),
		headers=self._control_headers)

            return query_request.json()

    def write(self, address, request, *args, **kwargs):
        self._logger.debug('Writing to thermostat> ')
        print "Write called!"
	print "address",address
        t = datetime.datetime.now()
        utc_seconds = (time.mktime(t.timetuple()))
        utc_seconds = int(utc_seconds * 1000)
        request['DeviceID'] = int(address)
	r=self._session.post(
	    'https://rs.alarmnet.com/TotalConnectComfort/Device/SubmitControlScreenChanges',
	    data=request,
	    headers=self._control_headers)

	#print "response:",r4.status,rawj,address
        if (r.status_code != 200): 
            print "Bad R4 status ", r.status_code, r.reason
            return False

	print "Okay!"
	self._logger.debug('Done >')

        return True

    def read(self, address=None, *args, **kwargs):
        self._login()
        return self._query(address)

    @property
    def username(self):
        return self._username


class HoneywellThermostat(HAInterface):
    VERSION = '0.0.4'

    FANAUTO = 0
    FANON = 1

    SYSTEMOFF = 2
    SYSTEMHEAT = 1
    SYSTEMCOOL = 3
    SYSTEMAUTO = 4


    def _init(self, *args, **kwargs):
        super(HoneywellThermostat, self)._init(*args, **kwargs)
        self._address = kwargs.get('address', None)

        self._cookie = None
        self._poll_secs = kwargs.get('poll', 360)
        self._iteration = self._poll_secs + 1
        self._retries = kwargs.get('retries', 5)

        self._username = self._interface.username

        self._fanMode = None                # 0-auto 1-on

        self._SetpointChangeAllowed = None
        #  off-false heat-true cool-true auto-true
        #  off-2     heat-1    cool-3    auto-4
        self._SystemSwitchPosition = None
        #  is Auto Heat/Cold allowed
        self._SwitchAutoAllowed = None

        self._last_temp = None
        self._CoolSetpoint = None
        self._HeatSetpoint = None
	self._setpoint = None
        self._StatusCool = None             # off-0 temp-1 perm-2
        self._StatusHeat = None             # off-0 temp-1 perm-2
        self._TemporaryHoldUntilTime = None  # minutes since midnight
        #value used when on temp
        #import datetime; str(timedelta(minutes=1410))
        self._request = {
            "DeviceID": int(self._address),
            "SystemSwitch": None,
            "HeatSetpoint": None,
            "CoolSetpoint": None,
            "HeatNextPeriod": None,
            "CoolNextPeriod": None,
            "StatusHeat": None,
            "StatusCool": None,
            "FanMode": None

        }
        """
        The "CoolNextPeriod" and "HeatNextPeriod" parameters require special
           explanation they represent the time at which you want to resume the
           normal program. They are represented as a "time-of-day". The number
           represents a time period of 15 minutes from midnight, (just as your
           thermostat can only allow you to set temporary holds which end on a
           15-minute boundary). So for example, if you wanted a temporary hold
           which ends at midnight - set the number to zero. If you wanted it to
           end a 12:15am, set it to 1. For 12:30am, set it to 2, etc. Needless
           to say, this allows you to only set temporary holds up to 24-hours.
           If no NextPeriod is specified however, this will effectively set a
           "permanent" hold, which must be subsequently manually candled.
        """

    def version(self):
        self._logger.info("Honeywell Thermostat Pytomation driver version "
                          + self.VERSION + '\n')

    def _readInterface(self, lastPacketHash):
        # Add a delay when querying the device to prevent abuse.

        if not self._iteration < self._poll_secs:
            self._iteration = 0
            self._logger.debug('DeviceId:' + self._address)
            #response = self._interface.read(address=self._address)
            #j = json.loads(response)
	    j = self._interface.read(address=self._address)
            fanData = j['latestData']['fanData']
            self._fanMode = fanData['fanMode']

            uiData = j['latestData']['uiData']
            current_temp = uiData["DispTemperature"]
            self._SetpointChangeAllowed = uiData["SetpointChangeAllowed"]
            self._SwitchAutoAllowed = uiData["SwitchAutoAllowed"]
            self._SystemSwitchPosition = uiData["SystemSwitchPosition"]
            self._CoolSetpoint = uiData["CoolSetpoint"]
            self._HeatSetpoint = uiData["HeatSetpoint"]
            self._StatusCool = uiData["StatusCool"]
            self._StatusHeat = uiData["StatusHeat"]
            self._TemporaryHoldUntilTime = uiData["TemporaryHoldUntilTime"]
	    
            print j
            #self._WeatherTemp = j['weather']['Temperature']

            if j['communicationLost'] == "True":
	        self.logger.error('Communication lost to thermostat>')
		
            state = None
	    self._logger.debug("Mode reported> "+str(self._SystemSwitchPosition))
            if self._SystemSwitchPosition == self.SYSTEMOFF:
                self._logger.debug("system off!")
                state = State.OFF

            elif self._SystemSwitchPosition == self.SYSTEMHEAT:
                self._logger.debug("heat on!")
                state = State.HEAT
                self._setpoint = self._HeatSetpoint

            elif self._SystemSwitchPosition == self.SYSTEMCOOL:
                self._logger.debug("cool on!")
                state = State.COOL
                self._setpoint = self._CoolSetpoint

            elif self._SystemSwitchPosition >= self.SYSTEMAUTO:
                state = State.AUTOMATIC
                if current_temp < self._HeatSetpoint:
                    self._logger.debug("auto: heat on!")
                    self._setpoint = self._HeatSetpoint
                elif current_temp > self._CoolSetpoint:
                    self._logger.debug("auto: cool on!")
		elif abs(self._HeatSetpoint - current_temp) < abs(self._CoolSetpoint - current_temp):
		    #closer to Heat than cool
		    self._logger.debug("auto: closer to needing heat")
		    self._setpoint = self._HeatSetpoint
		else:
		    self._logger.debug("auto: closer to needing cool")
		    self._setpoint = self._CoolSetpoint
            
	    self._logger.debug('State is> '+str(state))
            #self._onCommand(command=command, address=self._address)

            #f self._last_temp != current_temp:
	    #   self._logger.debug("Updating temp status")
                #elf._onCommand(
            #                   (Command.LEVEL, current_temp),
            #                   address=self._address 
            #                   )
            #self._onState(("temp",current_temp),address=self._address)
            self._onState(state=[("temp",current_temp),("setpoint",self._setpoint),("mode",state)],address=self._address)
            #self._onState(state=[("temp",current_temp),("setpoint",self._setpoint),("mode",state)],address=self._address)
	    

        else:
            self._iteration += 1
            time.sleep(1)  # one sec iteration

    def schedule(self, *args, **kwargs):  # should take us back to the schedule
        self._request['HeatSetPoint'] = 65
        self._request['StatusCool'] = 2
        self._request['StatusHeat'] = 2
        return self._interface.write(address=self._address,
                                     request=self._request)

    def automatic(self, *args, **kwargs):
        self._fan(mode="On")
        self._system(mode="Auto")
        return self._interface.write(address=self._address,
                                         request=self._request)

    def _fan(self, mode="On"):
        if mode == "On":
            self._request['FanMode'] = self.FANON
        else:
            self._request['FanMode'] = self.FANAUTO
        return

    def _system(self, mode="Auto"):
        if mode == "Auto":
            self._request['SystemSwitch'] = self.SYSTEMAUTO
        elif mode == "Cool":
            self._request['SystemSwitch'] = self.SYSTEMCOOL
        elif mode == "Heat":
            self._request['SystemSwitch'] = self.SYSTEMHEAT
        elif mode == "Off":
            self._request['SystemSwitch'] = self.SYSTEMOFF
        return

    def circulate(self, *args, **kwargs):
        self._fan(mode="On")
	print "Circ Devid: " + self._address, self._request
        return self._interface.write(address=self._address,
                                         request=self._request)

    def still(self, *args, **kwargs):
        self._fan(mode="Auto")
	print "Still Devid: " + self._address, self._request
        return self._interface.write(address=self._address,
                                         request=self._request)
        
    def setpoint(self, address, level, *args, **kwargs):
        if self._request['SystemSwitch'] == self.SYSTEMCOOL:
            self._request['CoolSetPoint'] = level
            
        if self._request['SystemSwitch'] == self.SYSTEMHEAT:
            self._request['HeatSetPoint'] = level  

	if self._request['SystemSwitch'] == self.SYSTEMAUTO:
	    if level < self._request['CoolSetPoint']:
	        self._request['CoolSetPoint'] = level
	    if level > self._request['HeatSetPoint']:
	        self._request['HeatSetPoint'] = level
	
	if self._request['SystemSwitch'] == self.SYSTEMOFF:
	    self.logger.error('Not right')

        return self._interface.write(address=self._address,
                                         request=self._request)     

    def status(self, *args, **kwargs):
        self._iteration = self._poll_secs + 1
	return 
