'''

File:
        ha_common.py

Description:
        Library of Home Automation code for Python


Author(s): 
         Jason Sharpee <jason@sharpee.com>  http://www.sharpee.com
        Pyjamasam <>

License:
    This free software is licensed under the terms of the GNU public license, Version 1     

Usage:
    - 


Example: (see bottom of file) 


Notes:
    - Common functionality between all of the classes I am implementing currently.

Created on Apr 3, 2011

@author: jason
'''

import threading
import traceback
import socket
import binascii
import serial
import hashlib
import sys
import urllib, urllib2
import requests

from pytomation.common.pytomation_object import PytomationObject


class Lookup(dict):
    """
    a dictionary which can lookup value by key, or keys by value
    # tested with Python25 by Ene Uran 01/19/2008    http://www.daniweb.com/software-development/python/code/217019
    """
    def __init__(self, items=[]):
        """items can be a list of pair_lists or a dictionary"""
        dict.__init__(self, items)

    def get_key(self, value):
        """find the key as a list given a value"""
        if type(value) == type(dict()):
            items = [item[0] for item in self.items() if item[1][value.items()[0][0]] == value.items()[0][1]]
        else:
            items = [item[0] for item in self.items() if item[1] == value]
        return items[0]

    def get_keys(self, value):
        """find the key(s) as a list given a value"""
        return [item[0] for item in self.items() if item[1] == value]

    def get_value(self, key):
        """find the value given a key"""
        return self[key]

class Command(object):
    ON = 'on'
    OFF = 'off'
    L10 = 'l10'
    L20 = 'l20'
    L30 = 'l30'
    L40 = 'l40'
    L50 = 'l50'
    L60 = 'l60'
    L70 = 'l70'
    L80 = 'l80'
    L90 = 'l90'
    LEVEL = 'level'
    SETPOINT = 'setpoint'
    PREVIOUS = 'previous'
    TOGGLE = 'toggle'
    BRIGHT = 'bright'
    DIM = 'dim'
    ACTIVATE = 'activate'
    DEACTIVATE = 'deactivate'
    INITIAL = 'initial'
    MOTION = 'motion'
    STILL = 'still'
    DARK = 'dark'
    LIGHT = 'light'
    OPEN = 'open'
    CLOSE = 'close'
    AUTOMATIC = 'automatic'
    MANUAL = 'manual'
    OCCUPY = 'occupy'
    VACATE = 'vacate'
    STATUS = 'status'
    VOICE = 'voice'
    COOL = 'cool'
    HEAT = 'heat'
    CIRCULATE = 'circulate'
    HOLD = 'hold'
    SCHEDULE = 'schedule'
    MESSAGE = 'message'

class Interface(PytomationObject):
    def __init__(self):
        self._disabled = False
        super(Interface, self).__init__()

    def read(self, bufferSize):
        raise NotImplemented

    def write(self, data):
        raise NotImplemented

    @property
    def disabled(self):
        return self._disabled

#class AsynchronousInterface(threading.Thread, Interface):
class AsynchronousInterface(Interface):
    def __init__(self, *args, **kwargs):
        #threading.Thread.__init__(self)
        #print 'AAAA' + str(args) + " : " + str(kwargs)
        super(AsynchronousInterface,self).__init__()
        
        self._logger.debug('Starting thread: ' + self.name)
#        self._main_thread = threading.Thread(target=self.run, args=(None,))
        self._main_thread = threading.Thread(target=self.run)
#        self.start()
        self._init(*args, **kwargs)
        self._main_thread.start()

    def _init(self, *args, **kwargs):
#        self.setDaemon(True)
        self._main_thread.setDaemon(True)

    def command(self,deviceId,command):
        raise NotImplementedError

    def onCommand(self,callback):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        pass
    
class TCP(Interface):
    def __init__(self, host, port):
        super(TCP, self).__init__()
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "connect %s:%s" % (host, port)
        self.__s.connect((host, port))

    def write(self,data):
        "Send raw binary"
        self.__s.send(data) 
        return None

    def read(self, bufferSize=4096):
        "Read raw data"
        data = ''
        try:
            data = self.__s.recv(bufferSize, socket.MSG_DONTWAIT)
        except socket.error, ex:
            pass
        except Exception, ex:
            print "Exception:", type(ex) 
            pass
#            print traceback.format_exc()
        return data

    def shutdown(self):
        self.__s.shutdown(socket.SHUT_RDWR)
        self.__s.close()


class TCP_old(Interface):
    def __init__(self, host, port):
        super(TCP_old, self).__init__()
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print"connect %s:%s" % (host, port)
        self.__s.connect((host, port))
        self.start()

    def send(self, dataString):
        "Send raw HEX encoded String"
        print "Data Sent=>" + dataString
        data = binascii.unhexlify(dataString)
        self.__s.send(data)
        return None

    def run(self):
        self._handle_receive()

    def _handle_receive(self):
        while 1:
            data = self.__s.recv(1024)
            self.c(data)
        self.__s.close()


class UDP(AsynchronousInterface):
    def __init__(self, fromHost, fromPort, toHost, toPort):
        super(UDP, self).__init__(fromHost,fromPort)
        self.__ssend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__ssend.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#        self.__srecv = socket(socket.AF_INET, socket.SOCK_DGRAM)
#        self.__srecv.bind((fromHost,fromPort))
        self.__ssend.bind((fromHost, fromPort))
        self.__fromHost = fromHost
        self.__fromPort = fromPort
        self.__toHost = toHost
        self.__toPort = toPort
        self.start()

    def send(self, dataString):
        self.__ssend.sendto(dataString,(self.__toHost, self.__toPort))
        return None

    def _handle_receive(self):
        while 1:
#            data = self.__srecv.recv(2048)
            data = self.__ssend.recv(2048)
            print "received stuff", data
            if self.c != None:
                self.c(data)

    def run(self):
        self._handle_receive()


class Serial(Interface):
    def __init__(self, serialDevicePath, serialSpeed=19200, serialTimeout=0.1, xonxoff=True, rtscts=False, dsrdtr=True):
        super(Serial, self).__init__()
        print "Using %s for serial communication" % serialDevicePath
#       self.__serialDevice = serial.Serial(serialDevicePath, 19200, timeout = 0.1) 
        try:
            self.__serialDevice = serial.Serial(serialDevicePath, serialSpeed, timeout = serialTimeout, rtscts=rtscts)
        except serial.serialutil.SerialException, ex:
            self._disabled = True
            self.__serialDevice = None
            self._logger.critical("{name} Could not open serial port.  Interface disabled".format(
                                                                                    name=self.name
                                                                                                  ))
        
    
    def read(self, bufferSize=1024):
        if self.__serialDevice:
            return self.__serialDevice.read(bufferSize)
        return ""

    def write(self, bytesToSend):
        if self.__serialDevice:
            return self.__serialDevice.write(bytesToSend)
        self._logger.critical("{name} Could not write to closed serial port".format(
                                                                    name=self.name
                                                                                    ))
        return True

    def inWaiting(self):
        if self.__serialDevice:
            return self.__serialDevice.inWaiting()
        return True

    def close(self):
        if self.__serialDevice:
            return self.__serialDevice.close()

class USB(Interface):
    def __init__(self, device):
        return None

class HTTP(Interface):
    def __init__(self, protocol='http', host=None, username=None, password=None):
        super(HTTP, self).__init__()

        self._protocol = protocol
        self._host = host
        self._username = username
        self._password = password
        self._logger.debug("{name} HTTP Port created".format(
                                                                                    name=self.name
                                                                                                  ))

    def request(self, path="", data=None, verb="GET"):
        _path = None
        _data = None
        _verb = None
        # If we are passed in all the params as a tuple in the first argument, decode
        if isinstance(path, tuple):
            try:
                _path = path[0]
                _data = path[1]
                _verb = path[2]
            except:
                pass
        else:
            _path = path
            _data = data
            _verb = verb

        if _verb == None:
            _verb = "GET"
# Expect the consumer to encode to allow for raw data formats      
#         if _data:
#             encdata = urllib.urlencode(_data)
#         else:
#             encdata = None

        url = self._protocol + "://" + self._host + "/" + _path
        r = getattr(requests, _verb.lower())
        
        response = False
        if self._username:
            response = r(url,
              data=_data,
              auth=requests.auth.HTTPBasicAuth(self._username, self._password))
        else:
            response = r(url,
              data=_data,
              )
            
        return response.text
# #         #print url + ":::" + _data
# #         r = urllib2.Request(url=url)
# #         r.add_data(_data)
# #         response = False
# #         try:
# #             response_stream = urllib2.urlopen(r)
# #     #        response_stream = urllib2.urlopen(url, _data)
# #             response = response_stream.read()
# #         except Exception, ex:
# #             self._logger.error('Could not request: ' + str(ex))
# #         #print url + ":" + str(_data) + ":" + str(response)
# #         return response

    def read(self, path="", data=None, verb='GET', *args, **kwargs):
        return self.request(path, data, verb)
        
    def write(self, path="", data=None, verb="POST", *args, **kwargs):
        if isinstance(path, tuple):
            _path = path[0]
            _data = path[1]
            _verb = 'POST'
        else:
            _path = path
            _data = data
            _verb = verb
        return self.request(_path, _data, _verb)

    def inWaiting(self):
        return True
    
    @property
    def host(self):
        return self._host

class HADevice(object):

    def __init__(self, deviceId, interface=None):
        super(HADevice,self).__init__()
        self.interface = interface
        self.deviceId = deviceId

    def set(self, command):
        self.interface.command(self, command)


class InsteonDevice(HADevice):
    def __init__(self, deviceId, interface=None):
        super(InsteonDevice, self).__init__(deviceId, interface)


class X10Device(HADevice):
    def __init__(self, deviceId, interface=None):
        super(X10Device, self).__init__(deviceId, interface)


class HACommand(Lookup):
    ON = 'on'
    OFF = 'off'

    def __init__(self):
        super(HACommand,self).__init__({
                       'on'         :{'primary' : {
                                                    'insteon':0x11,
                                                    'x10':0x02,
                                                    'upb':0x00
                                                  }, 
                                     'secondary' : {
                                                    'insteon':0xff,
                                                    'x10':None,
                                                    'upb':None
                                                    },
                                     },
                       'faston'    :{'primary' : {
                                                    'insteon':0x12,
                                                    'x10':0x02,
                                                    'upb':0x00
                                                  }, 
                                     'secondary' : {
                                                    'insteon':0xff,
                                                    'x10':None,
                                                    'upb':None
                                                    },
                                     },
                       'off'         :{'primary' : {
                                                    'insteon':0x13,
                                                    'x10':0x03,
                                                    'upb':0x00
                                                  }, 
                                     'secondary' : {
                                                    'insteon':0x00,
                                                    'x10':None,
                                                    'upb':None
                                                    },
                                     },

                       'fastoff'    :{'primary' : {
                                                    'insteon':0x14,
                                                    'x10':0x03,
                                                    'upb':0x00
                                                  }, 
                                     'secondary' : {
                                                    'insteon':0x00,
                                                    'x10':None,
                                                    'upb':None
                                                    },
                                     },
                       'level'    :{'primary' : {
                                                    'insteon':0x11,
                                                    'x10':0x0a,
                                                    'upb':0x00
                                                  }, 
                                     'secondary' : {
                                                    'insteon':0x88,
                                                    'x10':None,
                                                    'upb':None
                                                    },
                                     },
                       }
                      )
        pass


import time
import re


## {{{ http://code.activestate.com/recipes/142812/ (r1)
FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def hex_dump(src, length=8):
    N=0; result=''
    try:
        while src:
            s,src = src[:length],src[length:]
            hexa = ' '.join(["%02X"%ord(x) for x in s])
            s = s.translate(FILTER)
            result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
            N+=length
    except Exception, ex:
        print 'Exception in Hexdump: ' + str(ex)
        result = src
    return result

## end of http://code.activestate.com/recipes/142812/ }}}

def interruptibleSleep(sleepTime, interuptEvent):
    sleepInterval = 0.05

    #adjust for the time it takes to do our instructions and such
    totalSleepTime = sleepTime - 0.04

    while interuptEvent.isSet() == False and totalSleepTime > 0:
        time.sleep(sleepInterval)
        totalSleepTime = totalSleepTime - sleepInterval


def sort_nicely( l ):
    """ Sort the given list in the way that humans expect. 
    """ 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    l.sort( key=alphanum_key )

    return l

def convertStringFrequencyToSeconds(textFrequency):
    frequencyNumberPart = int(textFrequency[:-1])
    frequencyStringPart = textFrequency[-1:].lower()

    if (frequencyStringPart == "w"):
        frequencyNumberPart *= 604800
    elif (frequencyStringPart == "d"):
        frequencyNumberPart *= 86400
    elif (frequencyStringPart == "h"):
        frequencyNumberPart *= 3600
    elif (frequencyStringPart == "m"):
        frequencyNumberPart *= 60

    return frequencyNumberPart


def hashPacket(packetData):
    hash = None
    try:
        hash = hashlib.md5(packetData).hexdigest()
    except:
        hash = hashlib.md5(str(packetData)).hexdigest()
    return hash

# pylog replaces the "print" keyword to enable debugging and logging
def pylog(src, s):
    t = ""
    if logging:
        if logfileTimestamp != "":
            t = time.strftime(logfileTimestamp)
        try:
            if logfilePreserve:
                fp = open(logfile, "a")
            else:
                fp = open(logfile, "w")
        except Exception, ex:
            print "Log:" + t+ s + "\n"
#            print "ERROR Can't open log file..." + str(ex) + "=>"
#            try:
#                fp = open("/tmp/pylog.txt", "a")
#                print "Trying /tmp/pylog.txt"
#            except Exception, ex1:
#                sys.exit(0)
        else:
            fp.write(t + s + "\n")
            fp.close()
    else:
        print t + s


class Conversions(object):
    @staticmethod
    def hex_to_ascii(hex_string):
        return binascii.unhexlify(hex_string)

    @staticmethod
    def ascii_to_hex(hex_string):
        return binascii.hexlify(hex_string)

    @staticmethod
    def hex_to_bytes( hexStr ):
        """
        Convert a string hex byte values into a byte string. The Hex Byte values may
        or may not be space separated.
        """
        # The list comprehension implementation is fractionally slower in this case    
        #
        #    hexStr = ''.join( hexStr.split(" ") )
        #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
        #                                   for i in range(0, len( hexStr ), 2) ] )
     
        bytes = []
    
        hexStr = ''.join( hexStr.split(" ") )
    
        for i in range(0, len(hexStr), 2):
            bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )
    
        return ''.join( bytes )

    @staticmethod
    def int_to_ascii(integer):
#        ascii = str(unichr(integer))
        ascii = chr(integer)
        return ascii
    
    @staticmethod
    def hex_to_int(char):
        return Conversions.ascii_to_int(Conversions.hex_to_bytes(char))
    
    @staticmethod
    def int_to_hex(integer):
        return "%0.2X" % integer

    @staticmethod
    def ascii_to_int(char):
        return ord(char)

    ## http://code.activestate.com/recipes/142812/ }}}
    @staticmethod
    def hex_dump(src, length=8):
        result = ''
        try:
            N=0;
            while src:
                s,src = src[:length],src[length:]
                hexa = ' '.join(["%02X"%ord(x) for x in s])
                s = s.translate(FILTER)
                result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
                N+=length
        except Exception, ex:
            pass
        return result

    @staticmethod
    def checksum2(data):
        return reduce(lambda x,y:x+y, map(ord, data)) % 256    

    @staticmethod
    def checksum(data):
        cs = 0
        for byte in data:
            cs = cs + Conversions.ascii_to_int(byte)
        cs = ~cs
        cs = cs + 1
        cs = cs & 255
        return cs
        
