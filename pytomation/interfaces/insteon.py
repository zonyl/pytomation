'''
File:
        insteon.py

Description:
        InsteonPLM Home Automation Protocol library for Python (Smarthome 2412N, 2412S, 2412U)
        
        For more information regarding the technical details of the PLM:
                http://www.smarthome.com/manuals/2412sdevguide.pdf
                http://www.madreporite.com/insteon/commands.htm

Author(s): 
         Pyjamasam@github <>
         Jason Sharpee <jason@sharpee.com>  http://www.sharpee.com


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
    - Supports both 2412N and 2412S right now

Versions and changes:
    Initial version created on Mar 26 , 2011
    2012/11/14 - 1.1 - Added debug levels and global debug system
    2012/11/19 - 1.2 - Added logging, use pylog instead of print
    2012/11/30 - 1.3 - Unify Command and State magic strings across the system
    2012/12/09 - 1.4 - Been a lot of changes.. Bump
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

def _byteIdToStringId(idHigh, idMid, idLow):
    return '%02X.%02X.%02X' % (idHigh, idMid, idLow)


def _cleanStringId(stringId):
    return stringId[0:2] + stringId[3:5] + stringId[6:8]


def _stringIdToByteIds(stringId):
    return binascii.unhexlify(_cleanStringId(stringId))


def _buildFlags():
    #todo: impliment this
    return '\x0f'


def hashPacket(packetData):
    return hashlib.md5(packetData).hexdigest()


def simpleMap(value, in_min, in_max, out_min, out_max):
    #stolen from the arduino implimentation.  I am sure there is a nice python way to do it, but I have yet to stublem across it
    return (float(value) - float(in_min)) * (float(out_max) - float(out_min)) / (float(in_max) - float(in_min)) + float(out_min);


class InsteonPLM(HAInterface):
    VERSION = '1.4'
    
    #(address:engineVersion) engineVersion 0x00=i1, 0x01=i2, 0x02=i2cs
    deviceList = {};
    currentCommand = ""
    
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
                                    'responseSize': 22,
                                    'callBack':self._process_InboundExtendedInsteonMessage
                                  },
                                '52': { # Received X10
                                    'responseSize':3,
                                    'callBack':self._process_InboundX10Message
                                 },
                                '56': { # All Link Record Response
                                    'responseSize':5,
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

        self._insteonCommands = {
                                    #Direct Messages/Responses
                                    'SD03': {        #Product Data Request (generally an Ack)
                                        'callBack' : self._handle_StandardDirect_IgnoreAck
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
                                    #Broadcast Messages/Responses
                                    'SB01': {
                                                    #Set button pushed
                                        'callBack' : self._handle_StandardBroadcast_SetButtonPressed
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

        self._allLinkDatabase = dict()

    def _sendInterfaceCommand(self, modemCommand, commandDataString = None, extraCommandDetails = None):
        self.currentCommand = [modemCommand, commandDataString, extraCommandDetails]
        command = binascii.unhexlify(modemCommand)
        return super(InsteonPLM, self)._sendInterfaceCommand(command, commandDataString, extraCommandDetails, modemCommandPrefix='\x02')

    def _readInterface(self, lastPacketHash):
        #check to see if there is anyting we need to read
        firstByte = self._interface.read(1)
        if len(firstByte) == 1:
            #got at least one byte.  Check to see what kind of byte it is (helps us sort out how many bytes we need to read now)

            if firstByte[0] == '\x02':
                #modem command (could be an echo or a response)
                #read another byte to sort that out
                secondByte = self._interface.read(1)

                responseSize = -1
                callBack = None

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

                else:
                    self._logger.debug("No responseSize defined for modem command %s" % modemCommand)
            elif firstByte[0] == '\x15':
                self.nakRetries -= 1
                self._logger.debug("Received a Modem NAK! Retries left %d" % self.nakRetries)
                if self.nakRetries:
                    self._sendInterfaceCommand(self.currentCommand[0], self.currentCommand[1], self.currentCommand[2])
                else:
                    self._logger.debug("Too many NAK's! Device not responding...")
            else:
                self._logger.debug("Unknown first byte %s" % binascii.hexlify(firstByte[0]))
        else:
            #print "Sleeping"
            #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
            #time.sleep(0.1)
            time.sleep(0.5)

    def _sendStandardP2PInsteonCommand(self, destinationDevice, commandId1, commandId2):
        self.nakRetries = 3
        self._logger.debug("Command: %s %s %s" % (destinationDevice, commandId1, commandId2))
        return self._sendInterfaceCommand('62', _stringIdToByteIds(destinationDevice) + _buildFlags() + binascii.unhexlify(commandId1) + binascii.unhexlify(commandId2), extraCommandDetails = { 'destinationDevice': destinationDevice, 'commandId1': 'SD' + commandId1, 'commandId2': commandId2})

    def _sendStandardAllLinkInsteonCommand(self, destinationGroup, commandId1, commandId2):
        self.nakRetries = 3
        self._logger.debug("Command: %s %s %s" % (destinationGroup, commandId1, commandId2))
        return self._sendInterfaceCommand('61', binascii.unhexlify(destinationGroup) + binascii.unhexlify(commandId1) + binascii.unhexlify(commandId2))

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
        (modemCommand, idHigh, idMid, idLow, deviceCat, deviceSubCat, firmwareVer, acknak) = struct.unpack('xBBBBBBBB', responseBytes)
        #modemCommand = responseBytes[0]
        #idHigh = responseBytes[1] 
        #idMid = responseBytes[2] 
        #idLow = responseBytes[3] 
        #deviceCat = responseBytes[4] 
        #deviceSubCat = responseBytes[5] 
        #firmwareVer = responseBytes[6] 
        #acknak = responseBytes[7]
        
        foundCommandHash = None
        #find our pending command in the list so we can say that we're done (if we are running in syncronous mode - if not well then the caller didn't care)
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
#            if binascii.unhexlify(commandDetails['modemCommand']) == chr(modemCommand):
            if commandDetails['modemCommand'] == chr(modemCommand):
                #Looks like this is our command.  Lets deal with it
                self._commandReturnData[commandHash] = { 'id': _byteIdToStringId(idHigh,idMid,idLow), 'deviceCategory': '%02X' % deviceCat, 'deviceSubCategory': '%02X' % deviceSubCat, 'firmwareVersion': '%02X' % firmwareVer }    

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
        #we don't do anything here.  Just eat the echoed bytes
        pass

    def _process_StandardX10MessagePLMEcho(self, responseBytes):
        # Just ack / error echo from sending an X10 command
        pass

    def _validResponseMessagesForCommandId(self, commandId):
        if self._insteonCommands.has_key(commandId):
            commandInfo = self._insteonCommands[commandId]
            if commandInfo.has_key('validResponseCommands'):
                return commandInfo['validResponseCommands']

        return False

    def _process_InboundStandardInsteonMessage(self, responseBytes):
        (modemCommand, insteonCommand, fromIdHigh, fromIdMid, fromIdLow, toIdHigh, toIdMid, toIdLow, messageFlags, command1, command2) = struct.unpack('BBBBBBBBBBB', responseBytes)        
        #modemCommand = ord(responseBytes[0])
        #insteonCommand = ord(responseBytes[1])
        #fromIdHigh = ord(responseBytes[2])
        #fromIdMid = ord(responseBytes[3])
        #fromIdLow = ord(responseBytes[4])
        #toIdHigh = ord(responseBytes[5])
        #toIdMid = ord(responseBytes[6])
        #toIdLow = ord(responseBytes[7])
        #messageFlags = ord(responseBytes[8])
        #command1 = ord(responseBytes[9])
                
        #if len(responseBytes) > 10:
            #command2 = ord(responseBytes[10])
        #else:
        #    command2 = 0

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

        if insteonCommandCode == 'SD00':
            #this is a strange special case...
            #lightStatusRequest returns a standard message and overwrites the cmd1 and cmd2 bytes with "data"
            #cmd1 (that we use here to sort out what kind of incoming message we got) contains an 
            #"ALL-Link Database Delta number that increments every time there is a change in the addressee's ALL-Link Database"
            #which makes is super hard to deal with this response (cause cmd1 can likley change)
            #for now my testing has show that its 0 (at least with my dimmer switch - my guess is cause I haven't linked it with anything)
            #so we treat the SD00 message special and pretend its really a SD19 message (and that works fine for now cause we only really
            #care about cmd2 - as it has our light status in it)
            insteonCommandCode = 'SD19'

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
                    if validResponseMessages.count(insteonCommandCode) == 0:
                        #this pending command isn't waiting for a response with this command code...  Move along
                        continue
                else:
                    self._logger.warning("Unable to find a list of valid response messages for command %s" % originatingCommandId1)
                    continue


                #since there could be multiple insteon messages flying out over the wire, check to see if this one is from the device we send this command to
                destDeviceId = None
                if commandDetails.has_key('destinationDevice'):
                    destDeviceId = commandDetails['destinationDevice']

                if destDeviceId:
                    if destDeviceId.upper() == _byteIdToStringId(fromIdHigh, fromIdMid, fromIdLow).upper():

                        returnData = {} #{'isBroadcast': isBroadcast, 'isDirect': isDirect, 'isAck': isAck}

                        #try and look up a handler for this command code
                        if self._insteonCommands.has_key(insteonCommandCode):
                            if self._insteonCommands[insteonCommandCode].has_key('callBack'):
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
            self._logger.warning("This could be an unsolocicited broadcast message")

        if waitEvent and foundCommandHash:
            waitEvent.set()
            del self._pendingCommandDetails[foundCommandHash]
            self._logger.debug("Command %s completed\n" % foundCommandHash)

    def _process_InboundExtendedInsteonMessage(self, responseBytes):
        #51 
        #17 C4 4A     from
        #18 BA 62     to
        #50         flags
        #FF         cmd1
        #C0         cmd2
        #02 90 00 00 00 00 00 00 00 00 00 00 00 00    data
        pass
        #(modemCommand, insteonCommand, fromIdHigh, fromIdMid, fromIdLow, toIdHigh, toIdMid, toIdLow, messageFlags, command1, command2, data) = struct.unpack('BBBBBBBBBBB14s', responseBytes)        
                
    
    
    def _process_InboundX10Message(self, responseBytes):
        "Receive Handler for X10 Data"
        #X10 sends commands fully in two separate messages. Not sure how to handle this yet
        #TODO not implemented
        unitCode = None
        commandCode = None
        self._logger.debug("X10> " + hex_dump(responseBytes, len(responseBytes)))
             #       (insteonCommand, fromIdHigh, fromIdMid, fromIdLow, toIdHigh, toIdMid, toIdLow, messageFlags, command1, command2) = struct.unpack('xBBBBBBBBBB', responseBytes)        
#        houseCode =     (int(responseBytes[4:6],16) & 0b11110000) >> 4 
 #       houseCodeDec = X10_House_Codes.get_key(houseCode)
#        keyCode =       (int(responseBytes[4:6],16) & 0b00001111)
#        flag =          int(responseBytes[6:8],16)

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
        #02 50 17 C4 4A 18 BA 62 2B 00 00
        lightLevelRaw = messageBytes[10]

        #map the lightLevelRaw value to a sane value between 0 and 1
        normalizedLightLevel = simpleMap(ord(lightLevelRaw), 0, 255, 0, 1)

        return (True, {'lightStatus': round(normalizedLightLevel, 2) })

    #public methods
    def getPLMInfo(self, timeout = None):
        commandExecutionDetails = self._sendInterfaceCommand('60')

        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

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
        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '10', '00')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    def getInsteonEngineVersion(self, deviceId, timeout = None):
        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '0D', '00')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    def getProductData(self, deviceId, timeout = None):
        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '03', '00')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    def lightStatusRequest(self, deviceId, timeout = None):
        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '19', '00')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

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

    def on(self, deviceId, timeout = None):
        if len(deviceId) != 2: #insteon device address
            commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '11', 'ff')
        else: #X10 device address
            commandExecutionDetails = self._sendStandardP2PX10Command(deviceId,'02')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    def off(self, deviceId, timeout = None):
        if len(deviceId) != 2: #insteon device address
            commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '13', '00')
        else: #X10 device address
            commandExecutionDetails = self._sendStandardP2PX10Command(deviceId,'03')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
    
    def __getattr__(self, name):
        name = name.lower()
        # Support levels of lighting
        if name[0] == 'l' and len(name) == 3:
            level = name[1:3]
            level = int((int(level) / 100.0) * int(0xFF))
            return lambda x, y=None: self.level(x, level, timeout=y ) 
        
    def on_fast(self, deviceId, timeout = None):
        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '12', 'ff')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    def off_fast(self, deviceId, timeout=None):
        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '14', '00')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    def level(self, deviceId, level, timeout=None):

        #organize what dim level we are heading to (figgure out the byte we need to send)
        lightLevelByte = simpleMap(level, 0, 1, 0, 255)

        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '11', '%02x' % lightLevelByte)
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    def level_up(self, deviceId, timeout=None):
        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '15', '00')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    def level_down(self, deviceId, timeout=None):
        commandExecutionDetails = self._sendStandardP2PInsteonCommand(deviceId, '16', '00')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    # Activate scene with the address passed
    def active(self, address, timeout=None):
        commandExecutionDetails = self._sendStandardAllLinkInsteonCommand(address, '11', 'FF')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
        
    def inactive(self, address, timeout=None):
        commandExecutionDetails = self._sendStandardAllLinkInsteonCommand(address, '13', '00')
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)


    def update_scene(self, address, devices):
        # we are passed a scene number to update and a bunch of objects to update
        for device in devices:
            for k, v in device.iteritems():
                print 'This is a device member' + str(k)
        
    def version(self):
        self._logger.info("Insteon Pytomation driver version " + self.VERSION)


#**********************************************************************************************
#
#   Experimental Insteon link stuff
#
#-----------------------------------------------------------------------------------------------

    def scanDeviceVersions(self):
        for d in self._devices:
            r = self.getInsteonEngineVersion(d.address)
            print r
            time.sleep(1)


    def bitstring(self, s):
        return str(s) if s<=1 else self.bitstring(s>>1) + str(s&1)
    
    def _process_InboundAllLinkRecordResponse(self, responseBytes):
        print hex_dump(responseBytes)
        (modemCommand, insteonCommand, recordFlags, recordGroup, toIdHigh, toIdMid, toIdLow, linkData1, linkData2, linkData3) = struct.unpack('BBBBBBBBBB', responseBytes)
        print "    ALL-Link Record Flags: %s" % self.bitstring(recordFlags)
        print "    ALL-Link Group:        %d" % recordGroup
        print "    Link Data 1:           %d" % linkData1
        print "    Link Data 2:           %d" % linkData2
        print "    Link Data 3:           %d" % linkData3

    
    def print_linked_insteon_devices(self):
        for d in self._devices:
            print d.address
            print self.getInsteonEngineVersion(d.address)
            time.sleep(2)
            #print result['engineVersion']
            #self.getProductData(d.address)
                        
        #self.request_first_all_link_record()
        #while self.request_next_all_link_record():
        #    continue
       
    def request_first_all_link_record(self, timeout=None):
        commandExecutionDetails = self._sendInterfaceCommand('69')
        print "Sending Command 0x69..."
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)


    def request_next_all_link_record(self, timeout=None):
        commandExecutionDetails = self._sendInterfaceCommand('6A')
        print "Sending Command 0x6A..."
        return self._waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

