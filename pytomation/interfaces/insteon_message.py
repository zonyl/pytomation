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
from pytomation.interfaces.common import Command, PytomationObject

def _byteIdToStringId(idHigh, idMid, idLow):
    return '%02X.%02X.%02X' % (idHigh, idMid, idLow)

class InsteonMessage(PytomationObject):
    commands = {
        '0x11': Command.ON,
        '0x13': Command.OFF,
        '0x2e': None
    }

    def __init__(self, code, length):
        super(InsteonMessage, self).__init__()
        self._length = length
        self._data = []

    def appendData(self, value):
        self._data.append(value)

    def getData(self):
        return self._data
                
    def getLength(self):
        return self._length

    def _getCommands(self):
        return []

    def getCommands(self):
        commands = []
        try:
            commands = self._getCommands(self._data)
        except Exception as e:
            self._logger.debug("Exception %s" % e)
        
        commands = commands if commands else []
        return { 'data': self._data, 'commands': commands }

    def isComplete(self):
        return self.getLength() == len(self._data)
        
class InsteonEchoMessage(InsteonMessage):
    def __init__(self):
        super(InsteonEchoMessage, self).__init__(0x62, 9)

    def getLength(self):
        isExtended = len(self._data) >= 6 and (self._data[5] & 16 == 16)
        return 23 if isExtended else self._length

class InsteonExtendedMessage(InsteonMessage):
    def __init__(self):
        super(InsteonExtendedMessage, self).__init__(0x51, 25)
        
    def _getCommands(self):
        ledState = self._data[21]
        commands = []
        address = _byteIdToStringId(self._data[2], self._data[3], self._data[4])

        #led status
        for i in range(0,8):
            commands.append({'command': Command.ON if (ledState & (1 << i)) else Command.OFF, 'address': (address + ':%02X' % (i+1))})

        return commands

class InsteonStatusMessage(InsteonMessage):
    def __init__(self):
        super(InsteonStatusMessage, self).__init__(0x50, 11)
        
    def _commandFromLevel(self, level):
        command = Command.ON if level >= 250 else Command.OFF
        command = ((Command.LEVEL, level)) if level > 2 and level < 250 else command
        return command

    def _getCommands(self):
        flags = self._data[8]
        cmd1 = self._data[9]
        cmd2 = self._data[10]

        #Read the flags
        isAck = (flags & 32) == 32
        isGroup = (flags & 64) == 64
        isBroadcast = (flags & 128) == 128
        isDirectAck = isAck and not isGroup and not isBroadcast #ack from direct command (on,off,status,etc)
        isGroupCleanup = isGroup and not isAck and not isBroadcast #manually activated scene
        isGroupBroadcast = not isAck and isGroup and isBroadcast #manually activated scene
        isGroupAck = isAck and isGroup and not isBroadcast #plm activated scene ack of individual device
        
        address = _byteIdToStringId(self._data[2], self._data[3], self._data[4])
        commands = []
        command = None
        #lookup the command if we have it, though this isn't very reliable.
        if (hex(cmd1) in self.commands):
            command = self.commands[hex(self._data[9])]

        if (isDirectAck and cmd1 != 0x2e):
            #Set the on level from cmd2 since cmd1 is not consistent on status messages.
            #We ignore 0x2e here because that is an ACK for extended messages and is always 0.
            command = self._commandFromLevel(cmd2)
        elif (isGroupBroadcast):
            #group 1 means the main load of the switch was turned on.
            if (self._data[7] == 1):
                commands.append({'command': command, 'address': address})

            #This is a scene message, so we should notify the scene.
            address += ':%02X' % self._data[7]
        elif (isGroupCleanup and cmd2 != 0):
            #This is a scene message, so we should notify the scene.
            address += ':%02X' % cmd2
        elif (isGroupAck):
            #This is an All-Link Cleanup.  Notify the scene not the ack'ing device.
            address = '00.00.%02X' % cmd2

        commands.append({'command': command, 'address': address })

        return commands
