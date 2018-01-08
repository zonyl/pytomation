"""
File:
        w800rf32.py

Description:

This is a driver for the W800RF32 interface.  The W800 family of RF 
receivers are designed to receive X10 RF signals generated from X10 products: 
Palm Pad remotes, key chain remotes, Hawkeye motion detectors, and many, many 
other X10 RF devices.

The W800 then sends these commands directly to your computer's RS232 or 
USB port, depending on the model purchased. This allows your computer to 
receive X10 RF commands from remotes and motion detectors directly, without 
having to broadcast any power line commands, thus minimizing power line 
clutter and improving home automation response times by bypassing the usual 
power line delay.

This driver will re-initialize any of the boards that experience a power on 
reset or brownout without having to restart Pytomation.



Author(s):
         George Farris <farrisg@gmsys.com>
         Copyright (c), 2012
         
         Functions common to Pytomation written by:
         Jason Sharpee <jason@sharpee.com> 
         
License:
    This free software is licensed under the terms of the GNU public 
    license, Version 3

Usage:

    see /example_w800rf32_use.py

Notes:
    For documentation on the W800RF32 please see:
    http://www.wgldesigns.com/w800.html
    
Versions and changes:
    Initial version created on Oct 10 , 2012
    2012/11/14 - 1.1 - Added debug levels and global debug system
    2012/11/18 - 1.2 - Added logging
    2012/11/30 - 1.3 - Unify Command and State magic strings across the system
    2012/12/10 - 1.4 - New logging system
    2016/12/19 - 1.5 - Changed timeout Don't decode bytes 2 and 4, they are not required.
                       Add error check
"""
import threading
import time
import re
from Queue import Queue
from binascii import unhexlify

from .common import *
from .ha_interface import HAInterface

class W800rf32(HAInterface):
    VERSION = '1.5'
    MODEM_PREFIX = ''
    
    hcodeDict = {
0b0110:'A', 0b1110:'B', 0b0010:'C', 0b1010:'D',
0b0001:'E', 0b1001:'F', 0b0101:'G', 0b1101:'H',
0b0111:'I', 0b1111:'J', 0b0011:'K', 0b1011:'L',
0b0000:'M', 0b1000:'N', 0b0100:'O', 0b1100:'P'}

    houseCode = ""
    unitNunber = 0
    command = ""

    def __init__(self, interface, *args, **kwargs):
        super(W800rf32, self).__init__(interface, *args, **kwargs)
    
    def _init(self, *args, **kwargs):
        super(W800rf32, self)._init(*args, **kwargs)
        self.version()        


    def _readInterface(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read()
        
        if len(responses) >= 4:
            byte1 = ord(responses[0])
            byte2 = ord(responses[1])
            byte3 = ord(responses[2])
            byte4 = ord(responses[3])
            
            if byte1 + byte2 != 255 or byte3 + byte4 != 255:
                return
            xb3 = "{0:08b}".format(byte1)  # format binary string
            b3 = int(xb3[::-1],2)   # reverse the string and assign to byte 3
#            xb4 = "{0:08b}".format(byte2)  # format binary string
#            b4 = int(xb4[::-1],2)   # reverse the string and assign to byte 4
            xb1 = "{0:08b}".format(byte3)  # format binary string
            b1 = int(xb1[::-1],2)   # reverse the string and assign to byte 1
#            xb2 = "{0:08b}".format(byte4)  # format binary string
#            b2 = int(xb2[::-1],2)   # reverse the string and assign to byte 2

            # Get the house code
            self.houseCode = self.hcodeDict[b3 & 0x0f]

            # Next find unit number
            x = b1 >> 3
            x1 = (b1 & 0x02) << 1
            y = (b3 & 0x20) >> 2
            self.unitNumber = x + x1 + y + 1
            
            # Find command
            # 0x19 and 0x11 map to dim and bright but we don't support dim  and bright here so 
            # we map it to the illegal unit code "0". 0x11 and 0x19 will not map correctly
            # on all keypads.  4 unit keypads will have units 1 to 3 correct but unit 4 will be
            # 4 for "on" but 5 for "off".  Five unit keypads will be opposite, 5 will be "on" 
            # and 4 will be "off" but we already have a 4 "off".
            if b1 == 0x19:
                self.command = Command.OFF  
                self.unitNumber = 0         
            elif b1 == 0x11:                
                self.command = Command.ON
                self.unitNumber = 0
            elif b1 & 0x05 == 4:
                self.command = Command.OFF
            elif b1 & 0x05 == 0:
                self.command = Command.ON
            
            self.x10 = "%s%d" % (self.houseCode, self.unitNumber)
            self._logger.info("{0} - {1:02X},  {2} - {3:02X} - {4}".format(xb1, b1, xb3, b3, len(responses)))
            self._logger.info("Command -> " + self.x10 + " " + self.command )
                
            self._processDigitalInput(self.x10, self.command)
        elif len(responses) < 3 and len(responses) > 0:
            self._logger.error('Short packet...' + str(bytearray(responses)).encode('hex'))
        else:
#            too fast and we get multiple responses - consider it debounce
#            time.sleep(0.5)
            time.sleep(0.3)
                

    def _processDigitalInput(self, addr, cmd):
        self._onCommand(address=addr, command=cmd)


    def _processRegister(self, response, lastPacketHash):
        foundCommandHash = None

        #find our pending command in the list so we can say that we're done (if we are running in syncronous mode - if not well then the caller didn't care)
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
            if commandDetails['modemCommand'] == self._modemCommands['read_register']:
                #Looks like this is our command.  Lets deal with it
                self._commandReturnData[commandHash] = response[4:]

                waitEvent = commandDetails['waitEvent']
                waitEvent.set()

                foundCommandHash = commandHash
                break

        if foundCommandHash:
            del self._pendingCommandDetails[foundCommandHash]
        else:
            self._logger.warning("Unable to find pending command details for the following packet:")
            self._logger.warning(hex_dump(response) + " " + len(response))

    def _processNewW800RF32(self, response):
        pass

    def version(self):
        self._logger.info("W800RF32 Pytomation driver version " + self.VERSION)       
