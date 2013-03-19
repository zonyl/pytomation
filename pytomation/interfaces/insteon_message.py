'''
File:
    insteon_message.py

Description:
    A set of classes for Insteon support.

Author(s): 
    Chris Van Orman

License:
    This free software is licensed under the terms of the GNU public license, Version 1     

Usage:

Example: 

Notes:

Created on Mar 11, 2013
'''
import select
import traceback
import threading
import time
import binascii
import struct
import sys
import string
import hashlib
from collections import deque
from .common import *
from .ha_interface import HAInterface
from pytomation.devices import State

def _byteIdToStringId(idHigh, idMid, idLow):
    return '%02X.%02X.%02X' % (idHigh, idMid, idLow)


class InsteonStrategy(PytomationObject):
    commands = {
        '0x11': Command.ON,
        '0x13': Command.OFF,
        '0x2e': None
    }

    def __init__(self, code, length):
        super(InsteonStrategy, self).__init__()
        self._code = code
        self._length = length
        self._data = []

    def getLength(self, data):
       return self._length

    def _getCommands(self, data):
	    return []

    def getCommands(self, data):
        commands = []
        try:
            commands = self._getCommands(data)
        except Exception as e:
            self._logger.debug("Exception %s" % e)
        
        commands = commands if commands else []
        return { 'data': data, 'commands': commands }

    def isComplete(self, data):
        return self.getLength(data) == len(data)
        
class InsteonEchoStrategy(InsteonStrategy):
    def __init__(self):
        super(InsteonEchoStrategy, self).__init__(0x62, 9)

    def getLength(self, data):
        isExtended = len(data) >= 6 and (data[5] & 16 == 16)
        return 23 if isExtended else self._length

class InsteonExtendedStrategy(InsteonStrategy):
    def __init__(self):
        super(InsteonExtendedStrategy, self).__init__(0x51, 25)
        
    def _getCommands(self, data):
        ledState = data[21]
        commands = []
        address = _byteIdToStringId(data[2], data[3], data[4])

        #led status
        for i in range(0,8):
            commands.append({'command': Command.ON if (ledState & (1 << i)) else Command.OFF, 'address': (address + ':%02X' % (i+1))})

        return commands

class InsteonStatusStrategy(InsteonStrategy):
    def __init__(self):
        super(InsteonStatusStrategy, self).__init__(0x50, 11)
        
    def _commandFromLevel(self, level):
        command = Command.ON if level >= 250 else Command.OFF
        command = ((Command.LEVEL, level)) if level > 2 and level < 250 else command
        return command

    def _getCommands(self, data):
        flags = data[8]
        cmd1 = data[9]
        cmd2 = data[10]

        #Read the flags
        isAck = (flags & 32) == 32
        isGroup = (flags & 64) == 64
        isBroadcast = (flags & 128) == 128
        isDirectAck = isAck and not isGroup and not isBroadcast #ack from direct command (on,off,status,etc)
        isGroupCleanup = isGroup and not isAck and not isBroadcast #manually activated scene
        isGroupBroadcast = not isAck and isGroup and isBroadcast #manually activated scene
        isGroupAck = isAck and isGroup and not isBroadcast #plm activated scene ack of individual device
        
        address = _byteIdToStringId(data[2], data[3], data[4])
        commands = []
        command = None
        #lookup the command if we have it, though this isn't very reliable.
        if (hex(cmd1) in self.commands):
            command = self.commands[hex(data[9])]

        if (isDirectAck and cmd1 != 0x2e):
            #Set the on level from cmd2 since cmd1 is not consistent on status messages.
            #We ignore 0x2e here because that is an ACK for extended messages and is always 0.
            command = self._commandFromLevel(cmd2)
        elif (isGroupBroadcast):
            #group 1 means the main load of the switch was turned on.
            if (data[7] == 1):
                commands.append({'command': command, 'address': address})

            #This is a scene message, so we should notify the scene.
            address += ':%02X' % data[7]
        elif (isGroupCleanup and cmd2 != 0):
            #This is a scene message, so we should notify the scene.
            address += ':%02X' % cmd2
        elif (isGroupAck):
            #This is an All-Link Cleanup.  Notify the scene not the ack'ing device.
            address = '00.00.%02X' % cmd2

        commands.append({'command': command, 'address': address })

        return commands
	        
class InsteonMessage(PytomationObject):

    strategies = {
		0x15: InsteonStrategy(0x15, 1),
		0x50: InsteonStatusStrategy(),
		0x51: InsteonExtendedStrategy(),
		0x52: InsteonStrategy(0x52, 4),
		0x53: InsteonStrategy(0x53, 10),
		0x54: InsteonStrategy(0x54, 3),
		0x55: InsteonStrategy(0x55, 2),
		0x56: InsteonStrategy(0x56, 7),
		0x57: InsteonStrategy(0x57, 10),
		0x58: InsteonStrategy(0x58, 3),
		0x59: InsteonStrategy(0x59, 0),
		0x60: InsteonStrategy(0x60, 0),
		0x61: InsteonStrategy(0x61, 6),
		0x62: InsteonEchoStrategy(),
		0x63: InsteonStrategy(0x63, 5),
		0x64: InsteonStrategy(0x64, 5),
		0x65: InsteonStrategy(0x65, 3),
		0x66: InsteonStrategy(0x66, 6),
		0x67: InsteonStrategy(0x67, 3),
		0x68: InsteonStrategy(0x68, 4),
		0x69: InsteonStrategy(0x69, 3),
		0x6a: InsteonStrategy(0x6a, 3),
		0x6b: InsteonStrategy(0x6b, 4),
		0x6c: InsteonStrategy(0x6c, 3),
		0x6d: InsteonStrategy(0x6d, 3),
		0x6e: InsteonStrategy(0x6e, 3),
		0x6f: InsteonStrategy(0x6f, 12),
		0x70: InsteonStrategy(0x70, 4),
		0x71: InsteonStrategy(0x71, 5),
		0x72: InsteonStrategy(0x72, 3),
		0x73: InsteonStrategy(0x73, 6)
    }
	
    def __init__(self, *args, **kwargs):
        super(InsteonMessage, self).__init__(*args, **kwargs)
        self._data = []
        self._strategy = None

    def appendData(self, value):
        self._data.append(value)
        #look up our strategy
        if (len(self._data) == 2 or (len(self._data) == 1 and value == 0x15)):
            self._strategy = self.strategies[value]

    def isComplete(self):
        return self._strategy.isComplete(self._data) if self._strategy else False

    def getData(self):
        return self._data

    def getCommand(self):
		return self._strategy.getCommands(self._data) if self._strategy else None
