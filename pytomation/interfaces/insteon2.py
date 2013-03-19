'''
File:
        insteon2.py

Description:
    An Insteon driver for the Pytomation home automation framework.

Author(s): 
         Chris Van Orman

License:
    This free software is licensed under the terms of the GNU public license, Version 1     

Usage:


Example: 

Notes:
    Currently only tested with the 2412S, but should work with similar PLMs.

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
import array
from collections import deque
from .common import *
from .ha_interface import HAInterface
from .insteon_message import *
from .insteon_command import *
from pytomation.devices import State
from pytomation.devices import Scene

# _cleanStringId is for parsing a standard Insteon address such as 1E.2E.3E. It was taken from the original insteon.py.
def _cleanStringId(stringId):
    return stringId[0:2] + stringId[3:5] + stringId[6:8]

# _stringIdToByteIds is for parsing a standard Insteon address such as 1E.2E.3E. It was taken from the original insteon.py.
def _stringIdToByteIds(stringId):
    return binascii.unhexlify(_cleanStringId(stringId))
    
       
class InsteonPLM2(HAInterface):
    
    commands = {
        "on": InsteonStandardCommand([0x11,0xff]),
        "off": InsteonStandardCommand([0x13,0x00]),
        "status": InsteonStandardCommand([0x19, 0x00]),
        "ledstatus": InsteonExtendedCommand([0x2E, 0x00])
    }
    
    sceneCommands = {
        "on": InsteonAllLinkCommand([0x11,0x00]),
        "off": InsteonAllLinkCommand([0x13,0x00])
    }
    
    def __init__(self, interface, *args, **kwargs):
        super(InsteonPLM2, self).__init__(interface, *args, **kwargs)

    def _readInterface(self, lastPacketHash):
        #read all data from the underlying interface
        response = array.array('B', self._interface.read())
	
        if len(response) != 0:
            message = InsteonMessage()
            for b in response:
                if (message.isComplete()):
                    self._processMessage(message)
                    message = InsteonMessage()

                message.appendData(b)

            if (message.isComplete()):
                self._processMessage(message)
            else:
                self._printByteArray(message.getData(), "Incomplete")
				
    def _processMessage(self, message):
        self._printByteArray(message.getData())
        response = message.getCommand()
        
        if (response != None):
            command = response['commands']
            self._findPendingCommand(response['data'])
            
            for c in command:
                self._onCommand(command=c['command'], address=c['address'])
    
    def _findPendingCommand(self, data):
        #check if any commands are looking for this message
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
            command = commandDetails['command']
            if (command.isAck(data[1:])):
                self._commandReturnData[commandHash] = True
                waitEvent = commandDetails['waitEvent']
                waitEvent.set()

                del self._pendingCommandDetails[commandHash]
                self._logger.debug("Found pending command details")
                break

    def _printByteArray(self, data, message="Message"):
        s = ""
        for b in data: s += ' ' + hex(b)
        self._logger.debug(message + ">" + s + " <")	

    def command(self, device, command, timeout=None):
        command = command.lower()
#        deviceType = 'insteon' if isinstance(device, InsteonDevice) else 'x10'
        isScene = isinstance(device, Scene)
        
        commands = self.sceneCommands if isScene else self.commands
        
        try:
            haCommand = commands[command]
            
            #flags = 207 if isScene else 15
        
            haCommand.setAddress(array.array('B', _stringIdToByteIds(device.address)))
            #haCommand.setFlags(flags)
            commandExecutionDetails = self._sendInterfaceCommand(haCommand.getBytes(),
                extraCommandDetails = {'destinationDevice': device.deviceId, 'command' : haCommand})
            
            return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
        except:
            self._logger.exception('Error executing command')
            return None
        
    def on(self, deviceId, fast=None, timeout = None):
        self.command(self._getDevice(deviceId), Command.ON)

    def off(self, deviceId, fast=None, timeout=None):
        self.command(self._getDevice(deviceId), Command.OFF)

    def update_status(self):
        for d in self._devices:
            self.command(d, 'status')
                
    def _sendInterfaceCommand(self, modemCommand, commandDataString = None, extraCommandDetails = None):
        return super(InsteonPLM2, self)._sendInterfaceCommand(modemCommand, commandDataString, extraCommandDetails, modemCommandPrefix='\x02')

    def _getDevice(self, address):
        for d in self._devices:
            if (d.address == address): return d
        return None
