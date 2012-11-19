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
    
"""
import threading
import time
import re
from Queue import Queue
from binascii import unhexlify

from .common import *
from .ha_interface import HAInterface
from ..config import *

class W800rf32(HAInterface):
    VERSION = '1.2'
    MODEM_PREFIX = ''
    
    hcodeDict = {
0b0110:'A', 0b1110:'B', 0b0010:'C', 0b1010:'D',
0b0001:'E', 0b1001:'F', 0b0101:'G', 0b1101:'H',
0b0111:'I', 0b1111:'J', 0b0011:'K', 0b1011:'L',
0b0000:'M', 0b1000:'N', 0b0100:'O', 0b1100:'P'}

    houseCode = ""
    unitNunber = 0
    command = ""

    def __init__(self, interface):
        super(W800rf32, self).__init__(interface)
        if not debug.has_key('W800'):
            debug['W800'] = 0
        self.version()        
        self._modemRegisters = ""

        self._modemCommands = {
                               }

        self._modemResponse = {
                               }

    def _readModem(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read()
        if len(responses) != 0:
            x = "{0:08b}".format(ord(responses[0]))  # format binary string
            b3 = int(x[::-1],2)   # reverse the string and assign to byte 3
            x = "{0:08b}".format(ord(responses[1]))  # format binary string
            b4 = int(x[::-1],2)   # reverse the string and assign to byte 4
            x = "{0:08b}".format(ord(responses[2]))  # format binary string
            b1 = int(x[::-1],2)   # reverse the string and assign to byte 1
            x = "{0:08b}".format(ord(responses[3]))  # format binary string
            b2 = int(x[::-1],2)   # reverse the string and assign to byte 2
            if debug['W800'] > 0:
                pylog(self,"[W800RF32] {0:02X} {1:02X} {2:02X} {3:02X}\n".format(b1,b2,b3,b4))

            # Get the house code
            self.houseCode = self.hcodeDict[b3 & 0x0f]

            # Next find unit number
            x = b1 >> 3
            x1 = (b1 & 0x02) << 1
            y = (b3 & 0x20) >> 2
            self.unitNumber = x + x1 + y + 1
            
            # Find command
            if b1 == 0x19:
                self.command = 'DIM'
            elif b1 == 0x11:
                self.command = 'BRIGHT'
            elif b1 & 0x05 == 4:
                self.command = 'OFF'
            elif b1 & 0x05 == 0:
                self.command = 'ON'
            
            self.x10 = "%s%d" % (self.houseCode, self.unitNumber)
            if debug['W800'] > 0:
                pylog(self, "[W800RF32] Command -> " + self.x10 + " " + self.command + "\n")
                
            self._processDigitalInput(self.x10, self.command)

        else:
            time.sleep(0.5)
                
                

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
            pylog(self, "[W800RF32] Unable to find pending command details for the following packet:\n")
            pylog(self, hex_dump(response) + " " + len(response) + "n")

    def _processNewW800RF32(self, response):
        pass

    def version(self):
        pylog(self, "W800RF32 Pytomation driver version " + self.VERSION + "\n")
        
