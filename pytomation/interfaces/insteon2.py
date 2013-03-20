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
from pytomation.interfaces.common import Command
from pytomation.devices import Scene
from pytomation.interfaces.ha_interface import HAInterface
from pytomation.interfaces.insteon_command import InsteonStandardCommand, InsteonExtendedCommand, InsteonAllLinkCommand
from pytomation.interfaces.insteon_message import *
import array
import binascii

# _cleanStringId is for parsing a standard Insteon address such as 1E.2E.3E. It was taken from the original insteon.py.
def _cleanStringId(stringId):
    return stringId[0:2] + stringId[3:5] + stringId[6:8]

# _stringIdToByteIds is for parsing a standard Insteon address such as 1E.2E.3E. It was taken from the original insteon.py.
def _stringIdToByteIds(stringId):
    return binascii.unhexlify(_cleanStringId(stringId))
    
       
class InsteonPLM2(HAInterface):
    
    messages = {
        0x15: lambda : InsteonMessage(0x15, 1),
        0x50: lambda : InsteonStatusMessage(),
        0x51: lambda : InsteonExtendedMessage(),
        0x52: lambda : InsteonMessage(0x52, 4),
        0x53: lambda : InsteonMessage(0x53, 10),
        0x54: lambda : InsteonMessage(0x54, 3),
        0x55: lambda : InsteonMessage(0x55, 2),
        0x56: lambda : InsteonMessage(0x56, 7),
        0x57: lambda : InsteonMessage(0x57, 10),
        0x58: lambda : InsteonMessage(0x58, 3),
        0x59: lambda : InsteonMessage(0x59, 0),
        0x60: lambda : InsteonMessage(0x60, 0),
        0x61: lambda : InsteonMessage(0x61, 6),
        0x62: lambda : InsteonEchoMessage(),
        0x63: lambda : InsteonMessage(0x63, 5),
        0x64: lambda : InsteonMessage(0x64, 5),
        0x65: lambda : InsteonMessage(0x65, 3),
        0x66: lambda : InsteonMessage(0x66, 6),
        0x67: lambda : InsteonMessage(0x67, 3),
        0x68: lambda : InsteonMessage(0x68, 4),
        0x69: lambda : InsteonMessage(0x69, 3),
        0x6a: lambda : InsteonMessage(0x6a, 3),
        0x6b: lambda : InsteonMessage(0x6b, 4),
        0x6c: lambda : InsteonMessage(0x6c, 3),
        0x6d: lambda : InsteonMessage(0x6d, 3),
        0x6e: lambda : InsteonMessage(0x6e, 3),
        0x6f: lambda : InsteonMessage(0x6f, 12),
        0x70: lambda : InsteonMessage(0x70, 4),
        0x71: lambda : InsteonMessage(0x71, 5),
        0x72: lambda : InsteonMessage(0x72, 3),
        0x73: lambda : InsteonMessage(0x73, 6)
    }
    
    commands = {
        Command.ON: lambda : InsteonStandardCommand([0x11, 0xff]),
        Command.OFF: lambda : InsteonStandardCommand([0x13, 0x00]),
        Command.STATUS: lambda : InsteonStandardCommand([0x19, 0x00]),
        "ledstatus": lambda : InsteonExtendedCommand([0x2E, 0x00])
    }
    
    sceneCommands = {
        Command.ON: lambda : InsteonAllLinkCommand([0x11, 0x00]),
        Command.OFF: lambda : InsteonAllLinkCommand([0x13, 0x00])
    }
    
    def __init__(self, interface, *args, **kwargs):
        super(InsteonPLM2, self).__init__(interface, *args, **kwargs)

    def _readInterface(self, lastPacketHash):
        # read all data from the underlying interface
        response = array.array('B', self._interface.read())
        if len(response) != 0:
            message = None
            for b in response:
                # If no message found, check for a new one
                # exclude the start of text message 0x02
                if (not message and b != 0x2):
                    message = self.messages[b]()
                    
                # append the data to the message if it exists                    
                if (message):
                    message.appendData(b)
                
                # if our message is complete, then process it and 
                # start the next one
                if (message and message.isComplete()):
                    self._processMessage(message)
                    message = None

            # if we have a message then the last one was not complete
            if (message):
                self._printByteArray(message.getData(), "Incomplete")

    def _processMessage(self, message):
        self._printByteArray(message.getData())
        response = message.getCommand()
        
        if (response != None):
            command = response['commands']
            self._findPendingCommand(message)
            
            for c in command:
                self._onCommand(command=c['command'], address=c['address'])
    
    def _findPendingCommand(self, message):
        # check if any commands are looking for this message
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
            command = commandDetails['command']
            if (command.isAck(message)):
                self._commandReturnData[commandHash] = True
                waitEvent = commandDetails['waitEvent']
                waitEvent.set()

                del self._pendingCommandDetails[commandHash]
                self._logger.debug("Found pending command details")
                break

    def _printByteArray(self, data, message="Message"):
        s = ' '.join(hex(x) for x in data)
        self._logger.debug(message + ">" + s + " <")	

    def command(self, device, command, timeout=None):
        command = command.lower()
#        deviceType = 'insteon' if isinstance(device, InsteonDevice) else 'x10'
        isScene = isinstance(device, Scene)
        
        commands = self.sceneCommands if isScene else self.commands
        
        try:
            haCommand = commands[command]()
            
            # flags = 207 if isScene else 15
        
            haCommand.setAddress(array.array('B', _stringIdToByteIds(device.address)))
            # haCommand.setFlags(flags)
            commandExecutionDetails = self._sendInterfaceCommand(haCommand.getBytes(),
                extraCommandDetails={'destinationDevice': device.deviceId, 'command' : haCommand})
            
            return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)
        except:
            self._logger.exception('Error executing command')
            return None
        
    def on(self, deviceId, fast=None, timeout=None):
        self.command(self._getDevice(deviceId), Command.ON)

    def off(self, deviceId, fast=None, timeout=None):
        self.command(self._getDevice(deviceId), Command.OFF)

    def update_status(self):
        for d in self._devices:
            self.command(d, 'status')
                
    def _sendInterfaceCommand(self, modemCommand, commandDataString=None, extraCommandDetails=None):
        return super(InsteonPLM2, self)._sendInterfaceCommand(modemCommand, commandDataString, extraCommandDetails, modemCommandPrefix='\x02')

    def _getDevice(self, address):
        for d in self._devices:
            if (d.address == address): return d
        return None
