"""
Honeywell Thermostat Pytomation Interface

Author(s):
texnofobix@gmail.com

Idea/original code from:
Brad Goodman http://www.bradgoodman.com/  brad@bradgoodman.com

some code ideas from:
 George Farris <farrisg@gmsys.com>
"""
#import urllib2
import urllib
import json
import datetime
import re
#import time
#import math
#import base64
import time
import httplib

from .ha_interface import HAInterface
from .common import Interface, Command


class HoneywellWebsite(Interface):
    VERSION = '1.0.0'

    def __init__(self, username=None, password=None):
        super(HoneywellWebsite, self).__init__()

        self._host = "rs.alarmnet.com"
        self._username = username
        self._password = password
        self._cookie = None
        self._loggedin = False
        self._conn = None
        self._logger.debug('Created object for user> ' + str(username))
        try:
            self._login()
        except Exception, ex:
            self._logger.debug('Error logging in> ' + str(username)
                               + 'exception:' + ex)

    def _login(self):
        params = urllib.urlencode({"timeOffset": "240",
                                 "UserName": self._username,
                                 "Password": self._password,
                                 "RememberMe": "false"})

        headers = {"Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml," +
                "application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "sdch",
                "Host": "rs.alarmnet.com",
                "DNT": "1",
                "Origin": "https://rs.alarmnet.com/TotalComfort/",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) " +
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 " +
                " Safari/537.36"
            }
        self._conn = httplib.HTTPSConnection("rs.alarmnet.com")
        self._conn.request("POST", "/TotalConnectComfort/", params, headers)
        response = self._conn.getresponse()
        cookie = response.getheader("Set-Cookie")
        location = response.getheader("Location")
        newcookie = cookie
        newcookie = re.sub(";\s*expires=[^;]+", "", newcookie)
        newcookie = re.sub(";\s*path=[^,]+,", ";", newcookie)
        newcookie = re.sub("HttpOnly\s*[^;],", "X;", newcookie)
        newcookie = re.sub(";\s*HttpOnly\s*,", ";", newcookie)
        self._cookie = newcookie

        if ((location == None) or (response.status != 302)):
            self._logger.warning('Failed HTTP Code> ' + str(response.status))
            self._loggedin = False
        else:
            self._logger.debug('Login passed. HTTP Code> ' +
                               str(response.status))
            self._loggin = True

    def _query(self, deviceid):
        self._logger.debug('Querying Thermostat>')
        t = datetime.datetime.now()
        utc_seconds = (time.mktime(t.timetuple()))
        utc_seconds = int(utc_seconds * 1000)

        location = ("/TotalConnectComfort/Device/CheckDataSession/"
                    + deviceid + "?_=" + str(utc_seconds))
        headers = {
                "Accept": "*/*",
                "DNT": "1",
                "Accept-Encoding": "plain",
                "Cache-Control": "max-age=0",
                "Accept-Language": "en-US,en,q=0.8",
                "Connection": "keep-alive",
                "Host": "rs.alarmnet.com",
                "Referer": "https://rs.alarmnet.com/TotalConnectComfort/",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) " +
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 " +
                "Safari/537.36",
                "Cookie": self._cookie
            }
        self._conn = httplib.HTTPSConnection("rs.alarmnet.com")
        self._conn.request("GET", location, None, headers)
        r3 = self._conn.getresponse()
        if (r3.status != 200):
                self._logger.debug("Bad R3 status ")

        self._logger.debug(r3.status)
        self._logger.debug(r3.reason)
        return r3.read()

    def write(self, deviceid=None, request=None, *args, **kwargs):
        t = datetime.datetime.now()
        utc_seconds = (time.mktime(t.timetuple()))
        utc_seconds = int(utc_seconds * 1000)
        location = "/TotalConnectComfort/Device/SubmitControlScreenChanges"
        headers = {
            "Accept": 'application/json; q=0.01',
            "DNT": "1",
            "Accept-Encoding": "gzip,deflate,sdch",
            'Content-Type': 'application/json; charset=UTF-8',
            "Cache-Control": "max-age=0",
            "Accept-Language": "en-US,en,q=0.8",
            "Connection": "keep-alive",
            "Host": "rs.alarmnet.com",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/28.0.1500.95 Safari/537.36",
            'Referer': 'https://rs.alarmnet.com/TotalConnectComfort/' +
            'Device/Control/' + deviceid,
            "Cookie": self._cookie
        }

        request["DeviceID"] = int(deviceid)
        rawj = json.dumps(request)
        #self._logger.debug(location)
        #self._logger.debug(headers)
        #self._logger.debug(request)
        #self._logger.debug(rawj)

        self._conn = httplib.HTTPSConnection("rs.alarmnet.com")

        self._conn.request("POST", location, rawj, headers)
        r4 = self._conn.getresponse()
        if (r4.status != 200):
            print "Bad R4 status ", r4.status, r4.reason
            return False
        return True

    def read(self, deviceid=None, *args, **kwargs):
        return self._query(deviceid)

    @property
    def username(self):
        return self._username

    @property
    def cookie(self):
        return self._cookie


class HoneywellThermostat(HAInterface):
    VERSION = '0.9.0'

    def _init(self, *args, **kwargs):
        super(HoneywellThermostat, self)._init(*args, **kwargs)
        self._deviceid = kwargs.get('address', None)

        self._iteration = 0
        self._poll_secs = kwargs.get('poll', 360)
        self._retries = kwargs.get('retries', 5)

        self._username = self._interface.username
        self._cookie = self._interface.cookie

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
        self._StatusCool = None             # off-0 temp-1 perm-2
        self._StatusHeat = None             # off-0 temp-1 perm-2
        self._TemporaryHoldUntilTime = None  # minutes since midnight
        #value used when on temp
        #import datetime; str(timedelta(minutes=1410))
        self._request = {
            "DeviceID": self._deviceid,
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
            self._logger.debug('DeviceId:' + self._deviceid)
            response = self._interface.read(deviceid=self._deviceid)
            j = json.loads(response)
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

            command = None
            if self._SystemSwitchPosition == 2:
                self._logger.debug("system off!")
                command = Command.OFF

            elif self._SystemSwitchPosition == 1:
                self._logger.debug("heat on!")
                command = Command.HEAT
                self._setpoint = self._HeatSetpoint

            elif self._SystemSwitchPosition == 3:
                self._logger.debug("cool on!")
                command = Command.COOL
                self._setpoint = self._CoolSetpoint

            elif self._SystemSwitchPosition == 4:
                command = Command.AUTOMATIC
                if self._last_temp < self._HeatSetpoint:
                    self._logger.debug("auto: heat on!")
                    self._setpoint = self._HeatSetpoint
                elif self._last_temp > self._CoolSetpoint:
                    self._logger.debug("auto: cool on!")

            self._onCommand(command=command, address=self._deviceid)

            if self._last_temp != current_temp:
                self._onCommand(
                                (Command.LEVEL, current_temp),
                                address=self._deviceid
                                )
        else:
            self._iteration += 1
            time.sleep(1)  # one sec iteration

    def schedule(self, *args, **kwargs):  # should take us back to the schedule
        self._request['HeatSetPoint'] = 65
        self._request['StatusCool'] = 0
        self._request['StatusHeat'] = 0
        return self._interface.write(deviceid=self._deviceid,
                                     request=self._request)

    def automatic(self, *args, **kwargs):
        self._fan(mode="On")
        self._system(mode="Auto")
        return self._interface.write(deviceid=self._deviceid,
                                         request=self._request)

    def _fan(self, mode="On"):
        if mode == "On":
            self._request['FanMode'] = 1
        else:
            self._request['FanMode'] = 0
        return

    def _system(self, mode="Auto"):
        if mode == "Auto":
            self._request['SystemSwitch'] = 4
        elif mode == "Cool":
            self._request['SystemSwitch'] = 3
        elif mode == "Heat":
            self._request['SystemSwitch'] = 1
        elif mode == "Off":
            self._request['SystemSwitch'] = 2
        return

    def circulate(self, *args, **kwargs):
        self._fan(mode="On")
        return self._interface.write(deviceid=self._deviceid,
                                         request=self._request)

    def still(self, *args, **kwargs):
        self._fan(mode="Auto")
        return self._interface.write(deviceid=self._deviceid,
                                         request=self._request)

    def status(self, *args, **kwargs):
        self._iteration = self._poll_secs + 1
        return self._interface.write(deviceid=self._deviceid,
                                     request=self._request)

    def level(self, address, level, *args, **kwargs):
        print "Level called", level, address
        #Needs to be written
