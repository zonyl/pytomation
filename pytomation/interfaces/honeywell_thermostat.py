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
    VERSION = '0.0.1'

    def __init__(self, username=None, password=None):
        super(HoneywellWebsite, self).__init__()

        self._host = "rs.alarmnet.com"
        self._username = username
        self._password = password
        self._cookie = None
        self._loggedin = False
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
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "sdch",
                "Host": "rs.alarmnet.com",
                "DNT": "1",
                "Origin": "https://rs.alarmnet.com/TotalComfort/",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36"
            }
        conn = httplib.HTTPSConnection("rs.alarmnet.com")
        conn.request("POST", "/TotalConnectComfort/", params, headers)
        r1 = conn.getresponse()
        cookie = r1.getheader("Set-Cookie")
        location = r1.getheader("Location")
        newcookie = cookie
        newcookie = re.sub(";\s*expires=[^;]+", "", newcookie)
        newcookie = re.sub(";\s*path=[^,]+,", ";", newcookie)
        newcookie = re.sub("HttpOnly\s*[^;],", "X;", newcookie)
        newcookie = re.sub(";\s*HttpOnly\s*,", ";", newcookie)
        self._cookie = newcookie

        if ((location == None) or (r1.status != 302)):
            self._logger.warning('Failed HTTP Code> ' + str(r1.status))
            self._loggedin = False
        else:
            self._logger.debug('Login passed. HTTP Code> ' + str(r1.status))
            self._loggin = True

    def _query(self, deviceid):
            self._logger.debug('[HoneywellThermostat] Querying Thermostat>')
            t = datetime.datetime.now()
            utc_seconds = (time.mktime(t.timetuple()))
            utc_seconds = int(utc_seconds * 1000)

            location = "/TotalConnectComfort/Device/CheckDataSession/"
            + deviceid + "?_=" + str(utc_seconds)
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
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
                    "Cookie": self._cookie
                }
            conn = httplib.HTTPSConnection("rs.alarmnet.com")
            conn.request("GET", location, None, headers)
            r3 = conn.getresponse()
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
            "Referer": "https://rs.alarmnet.com/TotalConnectComfort/",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            'Referer': "/TotalConnectComfort/Device/CheckDataSession/" + deviceid,
            "Cookie": self._cookie
        }

        request["DeviceID"] = deviceid

        self._logger.debug(location)
        self._logger.debug(headers)
        self._logger.debug(request)
        return True

    def read(self, deviceid=None, *args, **kwargs):
        return self._query(deviceid)

    @property
    def username(self):
        return self._username


class HoneywellThermostat(HAInterface):
    VERSION = '0.0.2'

    def _init(self, *args, **kwargs):
        super(HoneywellThermostat, self)._init(*args, **kwargs)
        self._deviceid = kwargs.get('deviceid', None)

        self._cookie = None
        self._iteration = 0
        self._poll_secs = kwargs.get('poll', 360)
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
        self._StatusCool = None             # off-0 temp-1 perm-2
        self._StatusHeat = None             # off-0 temp-1 perm-2
        self._TemporaryHoldUntilTime = None  # minutes since midnight
        #value used when on temp
        #import datetime; str(timedelta(minutes=1410))
        self._request = {
            "CoolNextPeriod": None,
            "CoolSetpoint": 78,
            "DeviceID": None,
            "FanMode": None,
            "HeatNextPeriod": None,
            "HeatSetpoint": 70,
            "StatusCool": 0,
            "StatusHeat": 0,
            "SystemSwitch": None
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
        cancelHold = {
            "CoolNextPeriod": None,
            "CoolSetpoint": 75,  # bogus temp
            "DeviceID": None,
            "FanMode": None,
            "HeatNextPeriod": None,
            "HeatSetpoint": None,
            "StatusCool": 0,
            "StatusHeat": 0,
            "SystemSwitch": None
        }

        return self._interface.write(deviceid=self._deviceid,
                                     request=cancelHold)

    def automatic(self, *args, **kwargs):
        # should take us back to the schedule
        cancelHold = {
            "CoolNextPeriod": None,
            "CoolSetpoint": 75,  # bogus temp
            "DeviceID": None,
            "FanMode": None,
            "HeatNextPeriod": None,
            "HeatSetpoint": None,
            "StatusCool": 0,
            "StatusHeat": 0,
            "SystemSwitch": None
        }

        return self._interface.write(deviceid=self._deviceid,
                                         request=cancelHold)
