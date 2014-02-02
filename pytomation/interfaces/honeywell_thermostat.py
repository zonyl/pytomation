"""
Honeywell Thermostat Pytomation Interface

Author(s):
texnofobix@gmail.com

Idea/original code from:
Brad Goodman http://www.bradgoodman.com/  brad@bradgoodman.com

some code ideas from:
 George Farris <farrisg@gmsys.com>
"""
import urllib2
import urllib
import json
import datetime
import re
import time
import math
import base64
import time
import httplib
import sys
import tty,termios
import getopt
import os
import stat

from .ha_interface import HAInterface
from .common import *

class HoneywellThermostat(HAInterface):
    VERSION = '0.0.1'
    
    def __init__(self, *args, **kwargs):
        super(HoneywellThermostat, self).__init__(None, *args, **kwargs)
        
    def _init(self, *args, **kwargs):
        super(HoneywellThermostat, self)._init(*args, **kwargs)
        self._last_temp = None
        self._mode = None
        self._hold = None
        self._fan = None
        self._set_point = None
        self._away = None
        
        self._user_name = kwargs.get('username', None)
        self._password = kwargs.get('password', None)
        self._deviceid = kwargs.get('deviceid', None)
        
        self._cookie = None
        self._iteration = 0
        self._poll_secs = kwargs.get('poll', 360)
        self._retries = kwargs.get('retries', 5)

        try:
            #pass
	        self._login()
            
        except Exception, ex:
            self._logger.warning('Could not login: ' + str(ex))
        self._query()
        
    def version(self):
        self._logger.info("Honeywell Thermostat Pytomation driver version " + self.VERSION + '\n')
        
    def _login(self):
        params=urllib.urlencode({"timeOffset":"240",
                                 "UserName":self._user_name,
                                 "Password":self._password,
                                 "RememberMe":"false"})
        #print params
        headers={"Content-Type":"application/x-www-form-urlencoded",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding":"sdch",
                "Host":"rs.alarmnet.com",
                "DNT":"1",
                "Origin":"https://rs.alarmnet.com/TotalComfort/",
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36"
            }
        conn = httplib.HTTPSConnection("rs.alarmnet.com")
        conn.request("POST", "/TotalConnectComfort/",params,headers)
        r1 = conn.getresponse()
        #print r1.status, r1.reason
        cookie = r1.getheader("Set-Cookie")
        location = r1.getheader("Location")
        #print "Cookie",cookie
        #print
        # Strip "expires" "httponly" and "path" from cookie
        newcookie=cookie
        #newcookie=re.sub("^expires=[^;]+;","",newcookie)
        #newcookie=re.sub("^expires=[^;]+$","",newcookie)
        newcookie=re.sub(";\s*expires=[^;]+","",newcookie)
        #newcookie=re.sub("^path=[^;]+;","",newcookie)
        #newcookie=re.sub(";\s*path=[^;]+;",";",newcookie)
        newcookie=re.sub(";\s*path=[^,]+,",";",newcookie)
        newcookie=re.sub("HttpOnly\s*[^;],","X;",newcookie)
        newcookie=re.sub(";\s*HttpOnly\s*,",";",newcookie)
        self._cookie=newcookie
        #print "Cookie",cookie


        if ((location == None) or (r1.status != 302)):
            #raise BaseException("Login fail" )
            self._logger.warning('[HoneywellThermostat] Failed Code>'+str(r1.status))
        else:
            self._logger.debug('[HoneywellThermostat] Login passed>'+str(r1.status))
    
    def _query(self):
        temp = None
        self._logger.debug('[HoneywellThermostat] Querying Thermostat>')
        t = datetime.datetime.now()
        utc_seconds = (time.mktime(t.timetuple()))
        utc_seconds = int(utc_seconds*1000)
    
        location="/TotalConnectComfort/Device/CheckDataSession/"+self._deviceid+"?_="+str(utc_seconds)
        #print "THIRD"
        headers={
                "Accept":"*/*",
                "DNT":"1",
                #"Accept-Encoding":"gzip,deflate,sdch",
                "Accept-Encoding":"plain",
                "Cache-Control":"max-age=0",
                "Accept-Language":"en-US,en,q=0.8",
                "Connection":"keep-alive",
                "Host":"rs.alarmnet.com",
                "Referer":"https://rs.alarmnet.com/TotalConnectComfort/",
                "X-Requested-With":"XMLHttpRequest",
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
                "Cookie":self._cookie
            }
        conn = httplib.HTTPSConnection("rs.alarmnet.com")
        #conn.set_debuglevel(999);
        conn.request("GET", location,None,headers)
        r3 = conn.getresponse()
        if (r3.status != 200):
                print "Bad R3 status ",r3.status, r3.reason
        #print r3.status, r3.reason
        rawdata=r3.read()
        j = json.loads(rawdata)
        temp = j['latestData']['uiData']["DispTemperature"]
        self._logger.debug('[HoneywellThermostat] CurrentTemp>'+str(temp))
        self._last_temp = temp
#         if temp != self._last_temp:
        self._onCommand(command=(Command.LEVEL, int(temp))) #,address=self._deviceid
#         print json.dumps(j,sort_keys=True,indent=4, separators=(',', ': '))
#         print "Success",j['success']
#         print "Live",j['deviceLive']
#         print "CurrentTemp",j['latestData']['uiData']["DispTemperature"]
#         print "CoolSetpoint",j['latestData']['uiData']["CoolSetpoint"]
#         print "HeatSetpoint",j['latestData']['uiData']["HeatSetpoint"]
#         print "fanMode",j['latestData']['fanData']["fanMode"]
#         print "HoldUntil",j['latestData']['uiData']["TemporaryHoldUntilTime"]
#         print "StatusCool",j['latestData']['uiData']["StatusCool"]
#         print "StatusHeat",j['latestData']['uiData']["StatusHeat"]
    
    def _readInterface(self, lastPacketHash):
        # We need to dial back how often we check the thermostat.. Lets not bombard it!
        if not self._iteration < self._poll_secs:
            self._iteration = 0
#             check to see if there is anyting we need to read
#             responses = self._interface.read('tstat')
#             if len(responses) != 0:
#                 for response in responses.split():
#                     self._logger.debug("[HoneywellThermo] Response> " + hex_dump(response))
#                     self._process_current_temp(response)
#                     status = []
#                     try:
#                         status = json.loads(response)
#                     except Exception, ex:
#                         self._logger.error('Could not decode status request' + str(ex))
#                     self._process_mode(status)
            self._login()
            self._query()
            
            
        else:
            self._iteration+=1
            time.sleep(1) # one sec iteration

        
