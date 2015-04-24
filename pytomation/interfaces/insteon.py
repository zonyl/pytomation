'''
File:
        insteon.py

Description:
        InsteonPLM Home Automation Protocol library for Python (Smarthome 2412N, 2412S, 2412U)
        
        For more information regarding the technical details of the PLM:
                http://www.smarthome.com/manuals/2412sdevguide.pdf
                http://www.insteon.com/pdf/insteondetails.pdf (message flags)
                http://www.madreporite.com/insteon/commands.htm

Author(s): 
         Pyjamasam@github <>
         Jason Sharpee <jason@sharpee.com>  http://www.sharpee.com
         George Farris <farrisg@gmsys.com>

        Based loosely on the Insteon_PLM.pm code:
        -       Expanded by Gregg Liming <gregg@limings.net>

License:
    This free software is licensed under the terms of the GNU public license, Version 1     

Usage:
    - Instantiate InsteonPLM by passing in an interface
    - Call its methods
    - ?
    - Profit

Example: (see bottom of the file) 

Notes:
    - Supports 2412N, 2412S, and 2413U right now

Versions and changes:
    Initial version created on Mar 26 , 2011
    2012/11/14 - 1.1 - Added debug levels and global debug system
    2012/11/19 - 1.2 - Added logging, use pylog instead of print
    2012/11/30 - 1.3 - Unify Command and State magic strings across the system
    2012/12/09 - 1.4 - Been a lot of changes.. Bump
    2012/12/29 - 1.5 - Add support for turning scenes on and off
    2013/01/04 - 1.6 - Retry orphaned commands and deal with Modem Nak's
    2013/01/11 - 1.7 - Add status support from a linked device when manually operated
    2015/04/14 - 1.8 - Fixed status messages
    
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


def _cleanStringId(stringId):
    return stringId[0:2] + stringId[3:5] + stringId[6:8]


def _stringIdToByteIds(stringId):
    return binascii.unhexlify(_cleanStringId(stringId))


def _buildFlags(stdOrExt=None):
    #todo: impliment this
    if stdOrExt:
        return '\x1f'  # Extended command
    else:
        return '\x0f'  # Standard command


def hashPacket(packetData):
    return hashlib.md5(packetData).hexdigest()


def simpleMap(value, in_min, in_max, out_min, out_max):
    #stolen from the arduino implimentation.  I am sure there is a nice python way to do it, but I have yet to stublem across it
    return (float(value) - float(in_min)) * (float(out_max) - float(out_min)) / (float(in_max) - float(in_min)) + float(out_min);


'''
KEYPADLINC Information

D1   Button or Group number
D2   Controls sending data to device 
D3   Button's LED follow mask  - 0x00 - 0xFF
D4   Button's LED-off mask  - 0x00 - 0xFF
D5   X10 House code, we don't support
D6   X10 Unit code, we don't support
D7   Button's Ramp rate - 0x00 - 0x1F
D8   Button's ON Level  - 0x00 - 0xFF
D9   Global LED Brightness - 0x11 - 0x7F
D10  Non-toggle Bitmap If bit = 0, associated button is Toggle, If bit = 1, button is Non-toggle - 0x00 - 0xFF
D11  Button-LED State Bitmap If bit = 0, associated button's LED is Off, If bit = 1 button's LED is On - 0x00-0xFF
D12  X10 all bitmap
D13  Button Non-Toggle On/Off bitmap, 0 if non-toggle sends Off, 1 if non-toggle sends On
D14  Button Trigger-ALL-Link Bitmap If bit = 0, associated button sends normal Command If bit = 0, button sends ED 0x30 Trigger ALL-Link Command to first device in ALDB

D2 = 01  Is response to a get data request
     02  Set LED follow mask, D3 0x00-0xFF, D4-D14 unused set to 0x00
     03  Set LED off mask, D3 0x00-0xFF, D4-D14 unused set to 0x00
     04  Set X10 address for button - unsupported
     05  Set Ramp rate for button, D3 0x00-0x1F, D4-D14 unused set to 0x00
     06  Set ON Level for button, D3 0x00-0x1F, D4-D14 unused set to 0x00
     07  Set Global LED brightness, D3 0x11-0x7F, D4-D14 unused set to 0x00
     08  Set Non-Toggle state for button, D3 0x00-0x01, D4-D14 unused set to 0x00
     09  Set LED state for button, D3 0x00-0x01, D4-D14 unused set to 0x00
     0A  Set X10 all on - unsupported
     0B  Set Non-Toggle ON/OFF state for button, D3 0x00-0x01, D4-D14 unused set to 0x00
     0C  Set Trigger-ALL-Link State for button, D3 0x00-0x01, D4-D14 unused set to 0x00
     0D-FF Unused

00 01 20 00 00 20 00 00 3F 00 03 00 00 00  Main button ON
 1     3     5     7     9    11    13     A1 button ON

00 01 20 00 00 20 00 00 3F 00 C0 00 00 00  Main button OFF
00 01 20 00 00 20 00 00 3F 00 C4 00 00 00  A ON
00 01 20 00 00 20 00 00 3F 00 C8 00 00 00  B ON
00 01 20 00 00 20 00 00 3F 00 CC 00 00 00  A and B ON
00 01 20 00 00 20 00 00 3F 00 D0 00 00 00  C ON
00 01 20 00 00 20 00 00 3F 00 D4 00 00 00  A and C ON
00 01 20 00 00 20 00 00 3F 00 DC 00 00 00  A, B and C ON
'''

#class KeypadLinc():


class InsteonPLM(HAInterface):
    VERSION = '1.8'
    
    #(address:engineVersion) engineVersion 0x00=i1, 0x01=i2, 0x02=i2cs
    deviceList = {}         # Dynamically built list of devices [address,devcat,subcat,firmware,engine,name]
                            # we store and load this from disk and only run when network changes
    currentCommand = ""
    cmdQueueList = []   	# List of orphaned commands that need to be dealt with
    spinTime = 0.1   		# _readInterface loop time
    extendedCommand = False	# if extended command ack expected from PLM
    statusRequest = False   # Set to True when we do a status request
    lastUnit = ""		# last seen X10 unit code

    
    plmAddress = ""
    
    def __init__(self, interface, *args, **kwargs):
        super(InsteonPLM, self).__init__(interface, *args, **kwargs)
        
    def _init(self, *args, **kwargs):
        super(InsteonPLM, self)._init(*args, **kwargs)
        self.version()
        # Response sizes do not include the start of message (0x02) and the command
        self._modemCommands = {'60': {  # Get IM Info
                                    'responseSize': 7,
                                    'callBack':self._process_PLMInfo
                                  },
                                '61': { # Send All Link Command
                                    'responseSize': 4,
                                    'callBack':self._process_StandardInsteonMessagePLMEcho
                                  },
                                '62': { # Send Standard or Extended Message
                                    'responseSize': 7,
                                    'callBack':self._process_StandardInsteonMessagePLMEcho
                                  },
                                '63': { # Send X10
                                    'responseSize': 3,
                                    'callBack':self._process_StandardX10MessagePLMEcho
                                  },
                                '64': { # Start All Linking
                                    'responseSize': 3,
                                    'callBack':self._process_StandardInsteonMessagePLMEcho
                                  },
                                '65': { # Cancel All Linking
                                    'responseSize': 1,
                                    'callBack':self._process_StandardInsteonMessagePLMEcho
                                  },
                                '69': { # Get First All Link Record
                                    'responseSize': 1,
                                    'callBack':self._process_StandardInsteonMessagePLMEcho
                                  },
                                '6A': { # Get Next All Link Record
                                    'responseSize': 1,
                                    'callBack':self._process_StandardInsteonMessagePLMEcho
                                  },
                                '50': { # Received Standard Message
                                    'responseSize': 9,
                                    'callBack':self._process_InboundStandardInsteonMessage
                                  },
                                '51': { # Received Extended Message
                                    'responseSize': 23,
                                    'callBack':self._process_InboundExtendedInsteonMessage
                                  },
                                '52': { # Received X10
                                    'responseSize':3,
                                    'callBack':self._process_InboundX10Message
                                 },
                                '56': { # All Link Record Response
                                    'responseSize':4,
                                    'callBack':self._process_InboundAllLinkCleanupFailureReport
                                  },
                                '57': { # All Link Record Response
                                    'responseSize':8,
                                    'callBack':self._process_InboundAllLinkRecordResponse
                                  },
                                '58': { # All Link Record Response
                                    'responseSize':1,
                                    'callBack':self._process_InboundAllLinkCleanupStatusReport
                                  },
                            }
        self._modemExtCommands = {'62': { # Send Standard or Extended Message
                                    'responseSize': 21,
                                    'callBack':self._process_ExtendedInsteonMessagePLMEcho
                                  },
                            }

        self._insteonCommands = {
                                    #Direct Messages/Responses
                                    'SD03': {        #Product Data Request (generally an Ack)
                                        'callBack' : self._handle_StandardDirect_IgnoreAck,
                                        'validResponseCommands' : ['SD03']
                                    },
                                    'SD0D': {        #Get InsteonPLM Engine
                                        'callBack' : self._handle_StandardDirect_EngineResponse,
                                        'validResponseCommands' : ['SD0D']
                                    },
                                    'SD0F': {        #Ping Device
                                        'callBack' : self._handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD0F']
                                    },
                                    'SD10': {        #ID Request    (generally an Ack)
                                        'callBack' : self._handle_StandardDirect_IgnoreAck,
                                        'validResponseCommands' : ['SD10', 'SB01']
                                    },
                                    'SD11': {        #Devce On
                                        'callBack' : self._handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD11', 'SDFF', 'SD00']
                                    },
                                    'SD12': {        #Devce On Fast
                                        'callBack' : self._handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD12']
                                    },
                                    'SD13': {        #Devce Off
                                        'callBack' : self._handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD13']
                                    },
                                    'SD14': {        #Devce Off Fast
                                        'callBack' : self._handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD14']
                                    },
                                    'SD15': {        #Brighten one step
                                        'callBack' : self._handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD15']
                                    },
                                    'SD16': {        #Dim one step
                                        'callBack' : self._handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD16']
                                    },
                                    'SD19': {        #Light Status Response
                                        'callBack' : self._handle_StandardDirect_LightStatusResponse,
                                        'validResponseCommands' : ['SD19']
                                    },
                                    'SD2E': {        #Light Status Response
                                        'callBack' : self._handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD2E']
                                    },

				    #X10 Commands
                                    'XD03': {        #Light Status Response
                                        'callBack' : self._handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['XD03']
                                    },
                                    
                                    #Broadcast Messages/Responses
                                    'SB01': {
                                                    #Set button pushed
                                        'callBack' : self._handle_StandardBroadcast_SetButtonPressed
                                    },
                                    'SBXX12': {
                                                    #Fast On Command
                                        'callBack' : self._handle_StandardBroadcast_SetButtonPressed,
                                        'validResponseCommands' : ['SB12']
                                    },
                                    'SBXX14': {
                                                    #Fast Off Command
                                        'callBack' : self._handle_StandardBroadcast_SetButtonPressed,
                                        'validResponseCommands' : ['SB14']
                                    },

                                    #Unknown - Seems to be light level report
                                    'SDFF': {
                                             },
                                    'SD00': {
                                             },
                                }

        self._x10HouseCodes = Lookup(zip((
                            'm',
                            'e',
                            'c',
                            'k',
                            'o',
                            'g',
                            'a',
                            'i',
                            'n',
                            'f',
                            'd',
                            'l',
                            'p',
                            'h',
                            'n',
                            'j' ),xrange(0x0, 0xF)))

        self._x10UnitCodes = Lookup(zip((
                             '13',
                             '5',
                             '3',
                             '11',
                             '15',
                             '7',
                             '1',
                             '9',
                             '14',
                             '6',
                             '4',
                             '12',
                             '16',
                             '8',
                             '2',
                             '10'
                             ),xrange(0x0,0xF)))

        self._x10Commands = Lookup(zip((
                             'allUnitsOff',
                             'allLightsOn',
                             'on',
                             'off',
                             'dim',
                             'bright',
                             'allLightsOff',
                             'ext1',
                             'hail',
                             'hailAck',
                             'ext3',
                             'unused1',
                             'ext2',
                             'statusOn',
                             'statusOff',
                             'statusReq'
                             ),xrange(0x0,0xF)))

        self._allLinkDatabase = dict()
        self._intersend_delay = 0.85 #850ms between network sends

    def _sendInterfaceCommand(self, modemCommand, commandDataString = None, extraCommandDetails = None):
        self.currentCommand = [modemCommand, commandDataString, extraCommandDetails]
        command = binascii.unhexlify(modemCommand)
        return super(InsteonPLM, self)._sendInterfaceCommand(command, commandDataString, extraCommandDetails, modemCommandPrefix='\x02')

    def _readInterface(self, lastPacketHash):
        #check to see if there is anyting we need to read
        firstByte = self._interface.read(1)
        try:
            if len(firstByte) == 1:
                #got at least one byte.  Check to see what kind of byte it is (helps us sort out how many bytes we need to read now)
                
                if firstByte[0] == '\x02':
                    #modem command (could be an echo or a response)
                    #read another byte to sort that out
                    secondByte = self._interface.read(1)
    
                    responseSize = -1
                    callBack = None
                    
                    if self.extendedCommand:
                        # set the callback and response size expected for extended commands
                        modemCommand = binascii.hexlify(secondByte).upper()
                        if self._modemExtCommands.has_key(modemCommand):
                            if self._modemExtCommands[modemCommand].has_key('responseSize'):
                                responseSize = self._modemExtCommands[modemCommand]['responseSize']
                            if self._modemExtCommands[modemCommand].has_key('callBack'):
                                callBack = self._modemExtCommands[modemCommand]['callBack']

                    else:
                        # set the callback and response size expected for standard commands
                        modemCommand = binascii.hexlify(secondByte).upper()
                        if self._modemCommands.has_key(modemCommand):
                            if self._modemCommands[modemCommand].has_key('responseSize'):
                                responseSize = self._modemCommands[modemCommand]['responseSize']
                            if self._modemCommands[modemCommand].has_key('callBack'):
                                callBack = self._modemCommands[modemCommand]['callBack']
    
                    if responseSize != -1:
                        remainingBytes = self._interface.read(responseSize)
                        currentPacketHash = hashPacket(firstByte + secondByte + remainingBytes)
                        self._logger.debug("Receive< " + hex_dump(firstByte + secondByte + remainingBytes, len(firstByte + secondByte + remainingBytes)) + currentPacketHash + "\n")
    
                        if lastPacketHash and lastPacketHash == currentPacketHash:
                            #duplicate packet.  Ignore
                            pass
                        else:
                            if callBack:
                                callBack(firstByte + secondByte + remainingBytes)
                            else:
                                self._logger.debug("No callBack defined for for modem command %s" % modemCommand)
    
                        self._lastPacketHash = currentPacketHash
                        self.spinTime = 0.2     #reset spin time, there were no naks, Don't set this lower
                    else:
                        self._logger.debug("No responseSize defined for modem command %s" % modemCommand)
                        
                elif firstByte[0] == '\x15':
                    self.spinTime += 0.2
                    self._logger.debug("first byte %s" % binascii.hexlify(firstByte[0]))
                    self._logger.debug("Received a Modem NAK! Resending command, loop time %f" % (self.spinTime))
                    if self.spinTime < 12.0:
                        self._sendInterfaceCommand(self.currentCommand[0], self.currentCommand[1], self.currentCommand[2])
                    else:
                        self._logger.debug("Too many NAK's! Device not responding...")
                else:
                    self._logger.debug("Unknown first byte %s" % binascii.hexlify(firstByte[0]))
                
                self.extendedCommand = False	# go back to standard commands as default
                
            else:
                self._checkCommandQueue()
                #print "Sleeping"
                #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
                #time.sleep(0.1)
                time.sleep(self.spinTime)
        except TypeError, ex:
            pass

    def _sendStandardP2PInsteonCommand(self, destinationDevice, commandId1, commandId2):
        self._logger.debug("Command: %s %s %s" % (destinationDevice, commandId1, commandId2))
        return self._sendInterfaceCommand('62', _stringIdToByteIds(destinationDevice) + _buildFlags() + binascii.unhexlify(commandId1) + binascii.unhexlify(commandId2), extraCommandDetails = { 'destinationDevice': destinationDevice, 'commandId1': 'SD' + commandId1, 'commandId2': commandId2})

    def _sendStandardAllLinkInsteonCommand(self, destinationGroup, commandId1, commandId2):
        self._logger.debug("Command: %s %s %s" % (destinationGroup, commandId1, commandId2))
        return self._sendInterfaceCommand('61', binascii.unhexlify(destinationGroup) + binascii.unhexlify(commandId1) + binascii.unhexlify(commandId2),
                extraCommandDetails = { 'destinationDevice': destinationGroup, 'commandId1': 'SD' + commandId1, 'commandId2': commandId2})

    def _getX10UnitCommand(self,deviceId):
        "Send just an X10 unit code message"
        deviceId = deviceId.lower()
        return "%02x00" % ((self._x10HouseCodes[deviceId[0:1]] << 4) | self._x10UnitCodes[deviceId[1:2]])

    def _getX10CommandCommand(self,deviceId,commandCode):
        "Send just an X10 command code message"
        deviceId = deviceId.lower()
        return "%02x80" % ((self._x10HouseCodes[deviceId[0:1]] << 4) | int(commandCode,16))

    def _sendStandardP2PX10Command(self,destinationDevice,commandId1, commandId2 = None):
        # X10 sends 1 complete message in two commands
        self._logger.debug("Command: %s %s %s" % (destinationDevice, commandId1, commandId2))
        self._logger.debug("C: %s" % self._getX10UnitCommand(destinationDevice))
        self._logger.debug("c1: %s" % self._getX10CommandCommand(destinationDevice, commandId1))
            
        self._sendInterfaceCommand('63', binascii.unhexlify(self._getX10UnitCommand(destinationDevice)))

        return self._sendInterfaceCommand('63', binascii.unhexlify(self._getX10CommandCommand(destinationDevice, commandId1)))

    #low level processing methods
    def _process_PLMInfo(self, responseBytes):
        (modemCommand, InsteonCommand, idHigh, idMid, idLow, deviceCat, deviceSubCat, firmwareVer, acknak) = struct.unpack('BBBBBBBBB', responseBytes)
        
        foundCommandHash = None
        #find our pending command in the list so we can say that we're done (if we are running in syncronous mode - if not well then the caller didn't care)
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
#            if binascii.unhexlify(commandDetails['modemCommand']) == chr(modemCommand):
            if commandDetails['modemCommand'] == '\x60':
                #Looks like this is our command.  Lets deal with it
                #self._commandReturnData[commandHash] = { 'id': _byteIdToStringId(idHigh,idMid,idLow), 'deviceCategory': '%02X' % deviceCat, 'deviceSubCategory': '%02X' % deviceSubCat, 'firmwareVersion': '%02X' % firmwareVer }    
                self.plmAddress = _byteIdToStringId(idHigh,idMid,idLow).upper()
                
                waitEvent = commandDetails['waitEvent']
                waitEvent.set()

                foundCommandHash = commandHash
                break

        if foundCommandHash:
            del self._pendingCommandDetails[foundCommandHash]
        else:
            self._logger.warning("Unable to find pending command details for the following packet:")
            self._logger.warning(hex_dump(responseBytes, len(responseBytes)))

    def _process_StandardInsteonMessagePLMEcho(self, responseBytes):
        #print utilities.hex_dump(responseBytes, len(responseBytes))
        #echoed standard message is always 9 bytes with the 6th byte being the command
        #here we handle a status request as a special case the very next received message from the 
        #PLM will most likely be the status response.
        if ord(responseBytes[1]) == 0x62:
            if len(responseBytes) == 9:  # check for proper length
                if ord(responseBytes[6]) == 0x19 and ord(responseBytes[8]) == 0x06:  # get a light level status
                    self.statusRequest = True

    def _process_StandardX10MessagePLMEcho(self, responseBytes):
        # Just ack / error echo from sending an X10 command
        pass

    def _validResponseMessagesForCommandId(self, commandId):
        self._logger.debug('ValidResponseCheck: ' + hex_dump(commandId))
        if self._insteonCommands.has_key(commandId):
            commandInfo = self._insteonCommands[commandId]
            self._logger.debug('ValidResponseCheck2: ' + str(commandInfo))
            if commandInfo.has_key('validResponseCommands'):
                self._logger.debug('ValidResponseCheck3: ' + str(commandInfo['validResponseCommands']))
                return commandInfo['validResponseCommands']

        return False

    def _process_InboundStandardInsteonMessage(self, responseBytes):

        if len(responseBytes) != 11:
            self._logger.error("responseBytes< " + hex_dump(responseBytes, len(responseBytes)) + "\n")
            self._logger.error("Command incorrect length. Expected 11, Received %s\n" % len(responseBytes))
            return

        (modemCommand, insteonCommand, fromIdHigh, fromIdMid, fromIdLow, toIdHigh, toIdMid, toIdLow, messageFlags, command1, command2) = struct.unpack('BBBBBBBBBBB', responseBytes)
        foundCommandHash = None
        waitEvent = None

        #check to see what kind of message this was (based on message flags)
        isBroadcast = messageFlags & (1 << 7) == (1 << 7)
        isDirect = not isBroadcast
        isAck = messageFlags & (1 << 5) == (1 << 5)
        isNak = isAck and isBroadcast

        insteonCommandCode = "%02X" % command1
        if isBroadcast:
            #standard broadcast
            insteonCommandCode = 'SB' + insteonCommandCode
        else:
            #standard direct
            insteonCommandCode = 'SD' + insteonCommandCode

        if self.statusRequest:
            insteonCommandCode = 'SD19'
            
            #this is a strange special case...
            #lightStatusRequest returns a standard message and overwrites the cmd1 and cmd2 bytes with "data"
            #cmd1 (that we use here to sort out what kind of incoming message we got) contains an 
            #"ALL-Link Database Delta number that increments every time there is a change in the addressee's ALL-Link Database"
            #which makes is super hard to deal with this response (cause cmd1 can likley change)
            #for now my testing has show that its 0 (at least with my dimmer switch - my guess is cause I haven't linked it with anything)
            #so we treat the SD00 message special and pretend its really a SD19 message (and that works fine for now cause we only really
            #care about cmd2 - as it has our light status in it)
#            insteonCommandCode = 'SD19'

        #print insteonCommandCode

        #find our pending command in the list so we can say that we're done (if we are running in syncronous mode - if not well then the caller didn't care)
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
            #since this was a standard insteon message the modem command used to send it was a 0x62 so we check for that
#            if binascii.unhexlify(commandDetails['modemCommand']) == '\x62':
            if commandDetails['modemCommand'] == '\x62':
                originatingCommandId1 = None
                if commandDetails.has_key('commandId1'):
                    originatingCommandId1 = commandDetails['commandId1']

                validResponseMessages = self._validResponseMessagesForCommandId(originatingCommandId1)
                if validResponseMessages and len(validResponseMessages):
                    #Check to see if this received command is one that this pending command is waiting for
                    self._logger.debug('Valid Insteon Command COde: ' + str(insteonCommandCode))
                    if validResponseMessages.count(insteonCommandCode) == 0:
                        #this pending command isn't waiting for a response with this command code...  Move along
                        continue
                else:
                    self._logger.warning("Unable to find a list of valid response messages for command %s" % originatingCommandId1)
                    continue

                #since there could be multiple insteon messages flying out over the wire, check to see if this one is 
                #from the device we sent this command to
                destDeviceId = None
                if commandDetails.has_key('destinationDevice'):
                    destDeviceId = commandDetails['destinationDevice']

                if destDeviceId:
                    if destDeviceId.upper() == _byteIdToStringId(fromIdHigh, fromIdMid, fromIdLow).upper():

                        returnData = {} #{'isBroadcast': isBroadcast, 'isDirect': isDirect, 'isAck': isAck}

                        #try and look up a handler for this command code
                        if self._insteonCommands.has_key(insteonCommandCode):
                            if self._insteonCommands[insteonCommandCode].has_key('callBack'):
                                # Run the callback
                                (requestCycleDone, extraReturnData) = self._insteonCommands[insteonCommandCode]['callBack'](responseBytes)
                                self.statusRequest = False
                                
                                if extraReturnData:
                                    returnData = dict(returnData.items() + extraReturnData.items())

                                if requestCycleDone:
                                    waitEvent = commandDetails['waitEvent']
                            else:
                                self._logger.warning("No callBack for insteon command code %s" % insteonCommandCode)
                                waitEvent = commandDetails['waitEvent']
                        else:
                            self._logger.warning("No insteonCommand lookup defined for insteon command code %s" % insteonCommandCode)

                        if len(returnData):
                            self._commandReturnData[commandHash] = returnData

                        foundCommandHash = commandHash
                        break

        if foundCommandHash == None:
            self._logger.warning("Unhandled packet packet (couldn't find any pending command to deal with it)")
            self._logger.warning("This could be a status message from a broadcast")
            # very few things cause this certainly a scene on or off will so that's what we assume
            
            self._handle_StandardDirect_LightStatusResponse(responseBytes)

        if waitEvent and foundCommandHash:
            waitEvent.set()
            try:
                del self._pendingCommandDetails[foundCommandHash]
                self._logger.debug("Command %s completed\n" % foundCommandHash)
            except:
                self._logger.error("Command %s couldnt be deleted!\n" % foundCommandHash)

    def _process_InboundExtendedInsteonMessage(self, responseBytes):
        (modemCommand, insteonCommand, fromIdHigh, fromIdMid, fromIdLow, toIdHigh, toIdMid, toIdLow, messageFlags, \
            command1, command2, d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14) = struct.unpack('BBBBBBBBBBBBBBBBBBBBBBBBB', responseBytes)        
        
        print hex_dump(responseBytes)        

        foundCommandHash = None
        waitEvent = None
        
        return
        
        insteonCommandCode = "%02X" % command1
        insteonCommandCode = 'SD' + insteonCommandCode

        #find our pending command in the list so we can say that we're done (if we are running in syncronous mode - if not well then the caller didn't care)
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
            if commandDetails['modemCommand'] == '\x62':
                originatingCommandId1 = None
                if commandDetails.has_key('commandId1'):
                    originatingCommandId1 = commandDetails['commandId1']    #ex: SD03

                validResponseMessages = self._validResponseMessagesForCommandId(originatingCommandId1)
                if validResponseMessages and len(validResponseMessages):
                    #Check to see if this received command is one that this pending command is waiting for
                    if validResponseMessages.count(insteonCommandCode) == 0:
                        #this pending command isn't waiting for a response with this command code...  Move along
                        continue
                else:
                    self._logger.warning("Unable to find a list of valid response messages for command %s" % originatingCommandId1)
                    continue

                #since there could be multiple insteon messages flying out over the wire, check to see if this one is 
                #from the device we sent this command to
                destDeviceId = None
                if commandDetails.has_key('destinationDevice'):
                    destDeviceId = commandDetails['destinationDevice']

                if destDeviceId:
                    if destDeviceId.upper() == _byteIdToStringId(fromIdHigh, fromIdMid, fromIdLow).upper():

                        returnData = {} #{'isBroadcast': isBroadcast, 'isDirect': isDirect, 'isAck': isAck}

                        #try and look up a handler for this command code
                        if self._insteonCommands.has_key(insteonCommandCode):
                            if self._insteonCommands[insteonCommandCode].has_key('callBack'):
                                # Run the callback
                                (requestCycleDone, extraReturnData) = self._insteonCommands[insteonCommandCode]['callBack'](responseBytes)
                                
                                if extraReturnData:
                                    returnData = dict(returnData.items() + extraReturnData.items())

                                if requestCycleDone:
                                    waitEvent = commandDetails['waitEvent']
                            else:
                                self._logger.warning("No callBack for insteon command code %s" % insteonCommandCode)
                                waitEvent = commandDetails['waitEvent']
                        else:
                            self._logger.warning("No insteonCommand lookup defined for insteon command code %s" % insteonCommandCode)

                        if len(returnData):
                            self._commandReturnData[commandHash] = returnData

                        foundCommandHash = commandHash
                        break

        if foundCommandHash == None:
            self._logger.warning("Unhandled packet (couldn't find any pending command to deal with it)")
            self._logger.warning("This could be a status message from a broadcast")

        if waitEvent and foundCommandHash:
            waitEvent.set()
            del self._pendingCommandDetails[foundCommandHash]
            self._logger.debug("Command %s completed\n" % foundCommandHash)
    
 
    
    def _process_InboundX10Message(self, responseBytes):
        "Receive Handler for X10 Data"
        unitCode = None
        commandCode = None
        (byteB, byteC) = struct.unpack('xxBB', responseBytes)        
        self._logger.debug("X10> " + hex_dump(responseBytes, len(responseBytes)))
        houseCode =     (byteB & 0b11110000) >> 4 
        houseCodeDec = self._x10HouseCodes.get_key(houseCode)
        self._logger.debug("X10> HouseCode " + houseCodeDec )
        unitCmd = (byteC & 0b10000000) >> 7
        if unitCmd == 0 :
            unitCode = (byteB & 0b00001111)
            unitCodeDec = self._x10UnitCodes.get_key(unitCode)
            self._logger.debug("X10> UnitCode " + unitCodeDec )
            self.lastUnit = unitCodeDec
        else:
            commandCode = (byteB & 0b00001111)
            commandCodeDec = self._x10Commands.get_key(commandCode)
            self._logger.debug("X10> Command: house: " + houseCodeDec + " unit: " + self.lastUnit + " command: " + commandCodeDec  )
            destDeviceId = houseCodeDec.upper() + self.lastUnit
            if self._devices:
                for d in self._devices:
                    if d.address.upper() == destDeviceId:
                        # only run the command if the state is different than current
                        if (commandCode == 0x03 and d.state != State.OFF):     # Never seen one not go to zero but...
                            self._onCommand(address=destDeviceId, command=State.OFF)
                        elif (commandCode == 0x02 and d.state != State.ON):   # some times these don't go to 0xFF
                            self._onCommand(address=destDeviceId, command=State.ON)
            else: # No devices to check state, so send anyway
                if (commandCode == 0x03 ):     # Never seen one not go to zero but...
                    self._onCommand(address=destDeviceId, command=State.OFF)
                elif (commandCode == 0x02):   # some times these don't go to 0xFF
                    self._onCommand(address=destDeviceId, command=State.ON)

    #insteon message handlers
    def _handle_StandardDirect_IgnoreAck(self, messageBytes):
        #just ignore the ack for what ever command triggered us
        #there is most likley more data coming for what ever command we are handling
        return (False, None)

    def _handle_StandardDirect_AckCompletesCommand(self, messageBytes):
        #the ack for our command completes things.  So let the system know so
        return (True, None)

    def _handle_StandardBroadcast_SetButtonPressed(self, messageBytes):
        #02 50 17 C4 4A 01 19 38 8B 01 00
        (idHigh, idMid, idLow, deviceCat, deviceSubCat, deviceRevision) = struct.unpack('xxBBBBBBxxx', messageBytes)
        return (True, {'deviceType': '%02X%02X' % (deviceCat, deviceSubCat), 'deviceRevision':'%02X' % deviceRevision})

    def _handle_StandardDirect_EngineResponse(self, messageBytes):
        #02 50 17 C4 4A 18 BA 62 2B 0D 01
        engineVersionIdentifier = messageBytes[10]
        if engineVersionIdentifier == '\x00':
            return (True, {'engineVersion': 'i1'})
        elif engineVersionIdentifier == '\x01':
            return (True, {'engineVersion': 'i2'})
        elif engineVersionIdentifier == '\x02':
            return (True, {'engineVersion': 'i2cs'})
        else:
            return (True, {'engineVersion': 'FF'})

    def _handle_StandardDirect_LightStatusResponse(self, messageBytes):
        (modemCommand, insteonCommand, fromIdHigh, fromIdMid, fromIdLow, toIdHigh, toIdMid, toIdLow, messageFlags, command1, command2) = struct.unpack('BBBBBBBBBBB', messageBytes)

        destDeviceId = _byteIdToStringId(fromIdHigh, fromIdMid, fromIdLow).upper()
        self._logger.debug('HandleStandDirect')
        isGrpCleanupAck = (messageFlags & 0x60) == 0x60
        isGrpBroadcast = (messageFlags & 0xC0) == 0xC0
        isGrpCleanupDirect = (messageFlags & 0x40) == 0x40
        # If we get an ack from a group command fire off a status request or we'll never know the on level (not off)
        #0x06 = Reserved ... heartbeat?
        #0x11 = on
        #0x13 = off
        #0x19 = light status info (in command2)
        #0x17 = light level manual change START
        #0x18 = light level manual change STOP
        if (isGrpCleanupAck or isGrpBroadcast) and command1 != 0x13 and command1 !=0x11 and command1 != 0x19:
            if command1 != 0x06 and command1 != 0x17: #don't ask for status on a heartbeat or the start of a manual change
                self._logger.debug("Running status request:{0}:{1}:{2}:..........".format(isGrpCleanupAck, isGrpBroadcast, isGrpCleanupDirect))
                time.sleep(0.1)
                self.lightStatusRequest(destDeviceId, async=True)
        else: # direct command
            
            self._logger.debug("Setting status for:{0}:{1}:{2}..........".format(
                                                                                 str(destDeviceId),
                                                                                 str(command1),
                                                                                 str(command2),
                                                                                 ))
            if self._devices:
                for d in self._devices:
                    if d.address.upper() == destDeviceId:
                        # only run the command if the state is different than current
                        if command1 == 0x13:
                            if d.state != State.OFF:
                                self._onCommand(address=destDeviceId, command=State.OFF)
                        elif command1 == 0x11:
                            if d.state != State.ON:
                                if d.verify_on_level:
                                    self.lightStatusRequest(destDeviceId, async=True)
                                else:
                                    self._onCommand(address=destDeviceId, command=State.ON)
                        elif d.state != (State.LEVEL, command2):
                            if command2 < 0x02: #Off -- Doesn't always go to 0
                                if d.state != State.OFF: 
                                    self._onCommand(address=destDeviceId, command=State.OFF)
                            elif command2 > 0xFD: #On -- Doesn't always go to 255
                                if d.state != State.ON:
                                    self._onCommand(address=destDeviceId, command=State.ON)
                            else:
                                self._onCommand(address=destDeviceId, command=(State.LEVEL, int(command2 / 2.54)))
            else: # No devices to check state, so send anyway
                if command1 == 0x13:
                    if d.state != State.OFF:
                        self._onCommand(address=destDeviceId, command=State.OFF)
                elif command1 == 0x11:
                    if d.state != State.ON:
                        self._onCommand(address=destDeviceId, command=State.ON)
                elif command2:
                    if command2 < 0x02: #Off -- Doesn't always go to 0
                        self._onCommand(address=destDeviceId, command=State.OFF)
                    elif command2 > 0xFD: #On -- Doesn't always go to 255
                        self._onCommand(address=destDeviceId, command=State.ON)
                    else:
                        self._onCommand(address=destDeviceId, command=(State.LEVEL, int(command2 / 2.54)))
                
        self.statusRequest = False            
        return (True,None)
        # Old stuff, don't use this at the moment
        #lightLevelRaw = messageBytes[10]
        #map the lightLevelRaw value to a sane value between 0 and 1
        #normalizedLightLevel = simpleMap(ord(lightLevelRaw), 0, 255, 0, 1)

        #return (True, {'lightStatus': round(normalizedLightLevel, 2) })


   	# _checkCommandQueue is run every iteration of _readInterface. It counts the commands 
    # to find repeating ones.  If a command is repeated too many times it means it never
    # recieved a response so we should delete the original command and delete it from the 
    # queue.  This is a hack and will be dealt with properly in the new driver.
    def _checkCommandQueue(self):
        if self._pendingCommandDetails != {}:
            for (commandHash, commandDetails) in self._pendingCommandDetails.items():
                self.cmdQueueList.append(commandHash)
                
                # If we have an orphaned queue it will show up here, get the details, remove the old command
                # from the queue and re-issue.
                if self.cmdQueueList.count(commandHash) > 50:
                    if commandDetails['modemCommand'] in ['\x60','\x61','\x62']:
                        #print "deleting commandhash ", commandHash
                        #print commandDetails
                        cmd1 = commandDetails['commandId1']  # example SD11
                        cmd2 = commandDetails['commandId2']
                        deviceId = commandDetails['destinationDevice']
                        waitEvent = commandDetails['waitEvent']
                        waitEvent.set()
                        del self._pendingCommandDetails[commandHash]
                        while commandHash in self.cmdQueueList:
                            self.cmdQueueList.remove(commandHash)
                        # Retry the command..Do we really want this?
                        self._sendStandardP2PInsteonCommand(deviceId, cmd1[2:], cmd2)

    def __getattr__(self, name):
        name = name.lower()
        # Support levels of lighting
        if name[0] == 'l' and len(name) == 3:
            level = name[1:3]
            level = int((int(level) / 100.0) * int(0xFF))
            return lambda x, y=None: self.level(x, level, timeout=y ) 



    #---------------------------public methods---------------------------------
    
    def getPLMInfo(self, timeout = None):
        commandExecutionDetails = self._sendInterfaceCommand('60')

        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    # This doesn't work and ping in Insteon seems broken as far as I can tell.
    # The ping command 0x0D seems to return an ack from non-existant devices.
    def pingDevice(self, deviceId, timeout = None):
        startTime = time.time()
        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '0F', '00')

        #Wait for ping result
        commandReturnCode = self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
        endTime = time.time()

        if commandReturnCode:
            return endTime - startTime
        else:
            return False

    def idRequest(self, deviceId, timeout = None):
        if len(deviceId) != 2: #insteon device address
		commandExecutionDetails = self._sendExtendedP2PInsteonCommand(deviceId, '10', '00', '0')
		return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
	return

    def getInsteonEngineVersion(self, deviceId, timeout = None):
        if len(deviceId) != 2: #insteon device address
		commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '0D', '00')
		return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
	# X10 device,  command not supported,  just return
	return

    def getProductData(self, deviceId, timeout = None):
        if len(deviceId) != 2: #insteon device address
		commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '03', '00', )
		return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
	# X10 device,  command not supported,  just return
	return

    def lightStatusRequest(self, deviceId, timeout = None, async = False):
        if len(deviceId) != 2: #insteon device address
		commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '19', '00')
		if not async:
		    return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
		return
	# X10 device,  command not supported,  just return
	return

    def relayStatusRequest(self, deviceId, timeout = None):
        if len(deviceId) != 2: #insteon device address
		commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '19', '01')
		return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
	# X10 device,  command not supported,  just return
	return

    def command(self, device, command, timeout=None):
        command = command.lower()
        if isinstance(device, InsteonDevice):
            commandExecutionDetails = self._sendStandardP2PInsteonCommand(device.deviceId, "%02x" % (HACommand()[command]['primary']['insteon']), "%02x" % (HACommand()[command]['secondary']['insteon']))
            self._logger.debug("InsteonA" + commandExecutionDetails)
            
        elif isinstance(device, X10Device):
            commandExecutionDetails = self._sendStandardP2PX10Command(device.deviceId,"%02x" % (HACommand()[command]['primary']['x10']))
            self._logger.debug("X10A" + commandExecutionDetails)
        else:
            self._logger.debug("stuffing")
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    def on(self, deviceId, fast=None, timeout = None):
        if fast == 'fast':
            cmd = '12'
        else:
            cmd = '11'
        if len(deviceId) != 2: #insteon device address
            commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, cmd, 'ff')
        else: #X10 device address
            commandExecutionDetails = self._sendStandardP2PX10Command(deviceId,'02')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = 2.5)

    def off(self, deviceId, fast=None, timeout = None):
        if fast == 'fast':
            cmd = '14'
        else:
            cmd = '13'
        if len(deviceId) != 2: #insteon device address
            commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, cmd, '00')
        else: #X10 device address
            commandExecutionDetails = self._sendStandardP2PX10Command(deviceId,'03')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = 2.5)
    
      
    # if rate the bits 0-3 is 2 x ramprate +1, bits 4-7 on level + 0x0F
    def level(self, deviceId, level, rate=None, timeout=None):
        if level > 100 or level <0:
            self._logger.error("{name} cannot set light level {level} beyond 1-15".format(
                                                                                    name=self.name,
                                                                                    level=level,
                                                                                     ))
            return
        else:
            if rate == None:
                # make it 0 to 255                                                                                     
                level = int((int(level) / 100.0) * int(0xFF))
                commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '11', '%02x' % level)
                return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

            else:
                if rate > 15 or rate <1:
                    self._logger.error("{name} cannot set light ramp rate {rate} beyond 1-15".format(
                                                                                    name=self.name,
                                                                                    level=level,
                                                                                     ))
                    return
                else:
                    lev = int(simpleMap(level, 1, 100, 1, 15))                                                                                     
                    levelramp = (int(lev) << 4) + rate
                    commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '2E', '%02x' % levelramp)
                    return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    def level_up(self, deviceId, timeout=None):
        if len(deviceId) != 2: #insteon device address
            commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '15', '00')
            return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)
        # X10 device,  command not supported,  just return
        return

    def level_down(self, deviceId, timeout=None):
        if len(deviceId) != 2: #insteon device address
            commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '16', '00')
            return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)
        # X10 device,  command not supported,  just return
        return

    def status(self, deviceId, timeout=None):
        if len(deviceId) != 2: #insteon device address
            return self.lightStatusRequest(deviceId, timeout)
        # X10 device,  command not supported,  just return
        return

    # Activate scene with the address passed
    def active(self, address, timeout=None):
        if len(address) != 2: #insteon device address
            commandExecutionDetails = self._sendStandardAllLinkInsteonCommand(address, '12', 'FF')
            return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
        # X10 device,  command not supported,  just return
        return
        
    def inactive(self, address, timeout=None):
        if len(address) != 2: #insteon device address
            commandExecutionDetails = self._sendStandardAllLinkInsteonCommand(address, '14', '00')
            return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
        # X10 device,  command not supported,  just return
        return

    def update_status(self):
        for d in self._devices:
            if len(d.address) == 8:  # real address not scene
                print "Getting status for ", d.address
                self.lightStatusRequest(d.address)

    def update_scene(self, address, devices):
        # we are passed a scene number to update and a bunch of objects to update
        for device in devices:
            for k, v in device.iteritems():
                print 'This is a device member' + str(k)
        
    def version(self):
        self._logger.info("Insteon Pytomation driver version " + self.VERSION)


#**********************************************************************************************
#
#   Experimental Insteon stuff
#
#-----------------------------------------------------------------------------------------------
    # yeah of course this doesn't work cause Insteon has 5 year olds writing it's software.
    def getAllProductData(self):
        for d in self._devices:
            if len(d.address) == 8:  # real address not scene
                print "Getting product data for ", d.address
                self.RgetProductData(d.address)
                time.sleep(2.0)

    def getAllIdRequest(self):
        for d in self._devices:
            if len(d.address) == 8:  # real address not scene
                print "Getting product data for ", d.address
                self.idRequest(d.address)
                time.sleep(2.0)


        

    def bitstring(self, s):
        return str(s) if s<=1 else self.bitstring(s>>1) + str(s&1)

    def _sendExtendedP2PInsteonCommand(self, destinationDevice, commandId1, commandId2, d1_d14):
        self._logger.debug("Extended Command: %s %s %s %s" % (destinationDevice, commandId1, commandId2, d1_d14))
        self.extendedCommand = True
        return self._sendInterfaceCommand('62', _stringIdToByteIds(destinationDevice) + _buildFlags(self.extendedCommand) + binascii.unhexlify(commandId1) + binascii.unhexlify(commandId2), extraCommandDetails = { 'destinationDevice': destinationDevice, 'commandId1': 'SD' + commandId1, 'commandId2': commandId2})
    
    def _process_InboundAllLinkRecordResponse(self, responseBytes):
        #print hex_dump(responseBytes)
        (modemCommand, insteonCommand, recordFlags, recordGroup, toIdHigh, toIdMid, toIdLow, linkData1, linkData2, linkData3) = struct.unpack('BBBBBBBBBB', responseBytes)
        #keep the prints commented, for example format only
        #print "Device    Group Flags     Data1 Data2 Data3"
        #print "------------------------------------------------"
        print "%02x.%02x.%02x  %02x    %s  %d    %d    %d" % (toIdHigh, toIdMid, toIdLow, recordGroup,self.bitstring(recordFlags),linkData1, linkData2, linkData3)

    def _process_InboundAllLinkCleanupStatusReport(self, responseBytes):
        if responseBytes[2] == '\x06':
            self._logger.debug("All-Link Cleanup completed...")
            foundCommandHash = None
            waitEvent = None
            for (commandHash, commandDetails) in self._pendingCommandDetails.items():
                if commandDetails['modemCommand'] == '\x61':
                    originatingCommandId1 = None
                
                    if commandDetails.has_key('commandId1'):  #example SD11
                        originatingCommandId1 = commandDetails['commandId1']  # = SD11

                    if commandDetails.has_key('commandId2'):  #example FF
                        originatingCommandId2 = commandDetails['commandId2']
                
                    destDeviceId = None
                    if commandDetails.has_key('destinationDevice'):
                        destDeviceId = commandDetails['destinationDevice']
                
                    waitEvent = commandDetails['waitEvent']
                    foundCommandHash = commandHash
                    break

        if foundCommandHash == None:
            self._logger.warning("Unhandled packet (couldn't find any pending command to deal with it)")
            self._logger.warning("This could be an unsolocicited broadcast message")

        if waitEvent and foundCommandHash:
            time.sleep(1.0)  # wait for a bit befor resending the command.
            waitEvent.set()
            del self._pendingCommandDetails[foundCommandHash]
            
        else:
            self._logger.debug("All-Link Cleanup received a NAK...")


    # The group command failed, lets dig out the original command and issue a direct
    # command to the failed device. we will also delete the original command from pendingCommandDetails.
    def _process_InboundAllLinkCleanupFailureReport(self, responseBytes):
        (modemCommand, insteonCommand, deviceGroup, toIdHigh, toIdMid, toIdLow) = struct.unpack('BBBBBB', responseBytes)
        self._logger.debug("All-Link Cleanup Failure, resending command after 1 second...")
        #find our pending command in the list so we can say that we're done (if we are running in syncronous mode - if not well then the caller didn't care)
        foundCommandHash = None
        waitEvent = None
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
            if commandDetails['modemCommand'] == '\x61':
                originatingCommandId1 = None
                
                if commandDetails.has_key('commandId1'):  #example SD11
                    originatingCommandId1 = commandDetails['commandId1']  # = SD11

                if commandDetails.has_key('commandId2'):  #example FF
                    originatingCommandId2 = commandDetails['commandId2']
                
                destDeviceId = _byteIdToStringId(toIdHigh, toIdMid, toIdLow)
                #destDeviceId = None
                #if commandDetails.has_key('destinationDevice'):
                #    destDeviceId = commandDetails['destinationDevice']
                
                waitEvent = commandDetails['waitEvent']
                foundCommandHash = commandHash
                break

        if foundCommandHash == None:
            self._logger.warning("Unhandled packet (couldn't find any pending command to deal with it)")
            self._logger.warning("All Link - This could be an unsolocicited broadcast message")

        if waitEvent and foundCommandHash:
            waitEvent.set()
            del self._pendingCommandDetails[foundCommandHash]
            #self._sendStandardAllLinkInsteonCommand(destDeviceId, originatingCommandId1[2:], originatingCommandId2)
            self._sendStandardP2PInsteonCommand(destDeviceId, originatingCommandId1[2:], originatingCommandId2)
            
        
    
    def print_linked_insteon_devices(self):
        print "Device    Group Flags     Data1 Data2 Data3"
        print "------------------------------------------------"
        self.request_first_all_link_record()
        while self.request_next_all_link_record():
            time.sleep(0.1)
            
    def getkeypad(self):
        destinationDevice='12.BD.CA'
        commandId1='2E'
        commandId2='00'
        d1_d14='0000000000000000000000000000'
        self.extendedCommand = True
        return self._sendInterfaceCommand('62', _stringIdToByteIds(destinationDevice) + '\x1F' + 
                binascii.unhexlify(commandId1) + binascii.unhexlify(commandId2) + binascii.unhexlify(d1_d14), 
                extraCommandDetails = { 'destinationDevice': destinationDevice, 'commandId1': 'SD' + commandId1, 
                'commandId2': commandId2})

        
    def request_first_all_link_record(self, timeout=None):
        commandExecutionDetails = self._sendInterfaceCommand('69')
        #print "Sending Command 0x69..."
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)


    def request_next_all_link_record(self, timeout=None):
        commandExecutionDetails = self._sendInterfaceCommand('6A')
        #print "Sending Command 0x6A..."
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

