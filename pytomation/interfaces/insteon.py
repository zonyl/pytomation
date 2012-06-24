'''
File:
        insteon.py

Description:
        InsteonPLM Home Automation Protocol library for Python (Smarthome 2412N, 2412S, 2412U)
        
        For more information regarding the technical details of the PLM:
                http://www.smarthome.com/manuals/2412sdevguide.pdf

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
    - 
    - Todo: Read Style Guide @: http://www.python.org/dev/peps/pep-0008/

Created on Mar 26, 2011
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
from interfaces.common import *
from interfaces import HAInterface


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

    def __init__(self, interface):
        super(InsteonPLM, self).__init__(interface)

        self._modemCommands = {'60': {
                                    'responseSize': 7,
                                    'callBack':self.__process_PLMInfo
                                  },
                                '62': {
                                    'responseSize': 7,
                                    'callBack':self.__process_StandardInsteonMessagePLMEcho
                                  },

                                '50': {
                                    'responseSize': 9,
                                    'callBack':self.__process_InboundStandardInsteonMessage
                                  },
                                '51': {
                                    'responseSize': 23,
                                    'callBack':self.__process_InboundExtendedInsteonMessage
                                  },
                                '63': {
                                    'responseSize': 4,
                                    'callBack':self.__process_StandardX10MessagePLMEcho
                                  },
                                '52': {
                                    'responseSize':4,
                                    'callBack':self.__process_InboundX10Message
                                 },
                            }

        self._insteonCommands = {
                                    #Direct Messages/Responses
                                    'SD03': {        #Product Data Request (generally an Ack)
                                        'callBack' : self.__handle_StandardDirect_IgnoreAck
                                    },
                                    'SD0D': {        #Get InsteonPLM Engine
                                        'callBack' : self.__handle_StandardDirect_EngineResponse,
                                        'validResponseCommands' : ['SD0D']
                                    },
                                    'SD0F': {        #Ping Device
                                        'callBack' : self.__handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD0F']
                                    },
                                    'SD10': {        #ID Request    (generally an Ack)
                                        'callBack' : self.__handle_StandardDirect_IgnoreAck,
                                        'validResponseCommands' : ['SD10', 'SB01']
                                    },
                                    'SD11': {        #Devce On
                                        'callBack' : self.__handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD11']
                                    },
                                    'SD12': {        #Devce On Fast
                                        'callBack' : self.__handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD12']
                                    },
                                    'SD13': {        #Devce Off
                                        'callBack' : self.__handle_StandardDirect_AckCompletesCommand.
                                        'validResponseCommands' : ['SD13']
                                    },
                                    'SD14': {        #Devce Off Fast
                                        'callBack' : self.__handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD14']
                                    },
                                    'SD15': {        #Brighten one step
                                        'callBack' : self.__handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD15']
                                    },
                                    'SD16': {        #Dim one step
                                        'callBack' : self.__handle_StandardDirect_AckCompletesCommand,
                                        'validResponseCommands' : ['SD16']
                                    },
                                    'SD19': {        #Light Status Response
                                        'callBack' : self.__handle_StandardDirect_LightStatusResponse,
                                        'validResponseCommands' : ['SD19']
                                    },
                                    #Broadcast Messages/Responses
                                    'SB01': {
                                                    #Set button pushed
                                        'callBack' : self.__handle_StandardBroadcast_SetButtonPressed
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

    def __sendModemCommand(self, modemCommand, commandDataString = None, extraCommandDetails = None):
        command = '\x02' + binascii.unhexlify(modemCommand)
        super(InsteonPLM, self).__sendModemCommand(self, command, commandDataString, extraCommandDetails)

    def _readModem(self, lastPacketHash):
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

                    print "< ",
                    print hex_dump(firstByte + secondByte + remainingBytes, len(firstByte + secondByte + remainingBytes)),

                    currentPacketHash = hashPacket(firstByte + secondByte + remainingBytes)
                    if lastPacketHash and lastPacketHash == currentPacketHash:
                        #duplicate packet.  Ignore
                        pass
                    else:
                        if callBack:
                            callBack(firstByte + secondByte + remainingBytes)
                        else:
                            print "No callBack defined for for modem command %s" % modemCommand

                    lastPacketHash = currentPacketHash

                else:
                    print "No responseSize defined for modem command %s" % modemCommand
            elif firstByte[0] == '\x15':
                print "Received a Modem NAK!"
            else:
                print "Unknown first byte %s" % binascii.hexlify(firstByte[0])
        else:
            #print "Sleeping"
            #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
            #time.sleep(0.1)
            time.sleep(0.5)


    def __sendStandardP2PInsteonCommand(self, destinationDevice, commandId1, commandId2):
        print "Command: %s %s %s" % (destinationDevice, commandId1, commandId2)
        return self.__sendModemCommand('62', _stringIdToByteIds(destinationDevice) + _buildFlags() + binascii.unhexlify(commandId1) + binascii.unhexlify(commandId2), extraCommandDetails = { 'destinationDevice': destinationDevice, 'commandId1': 'SD' + commandId1, 'commandId2': commandId2})

    def __getX10UnitCommand(self,deviceId):
        "Send just an X10 unit code message"
        deviceId = deviceId.lower()
        return "%02x00" % ((self.__x10HouseCodes[deviceId[0:1]] << 4) | self.__x10UnitCodes[deviceId[1:2]])

    def __getX10CommandCommand(self,deviceId,commandCode):
        "Send just an X10 command code message"
        deviceId = deviceId.lower()
        return "%02x80" % ((self.__x10HouseCodes[deviceId[0:1]] << 4) | int(commandCode,16))

    def __sendStandardP2PX10Command(self,destinationDevice,commandId1, commandId2 = None):
        # X10 sends 1 complete message in two commands
        print "Command: %s %s %s" % (destinationDevice, commandId1, commandId2)
        print "C: %s" % self.__getX10UnitCommand(destinationDevice)
        print "c1: %s" % self.__getX10CommandCommand(destinationDevice, commandId1)
        self.__sendModemCommand('63', binascii.unhexlify(self.__getX10UnitCommand(destinationDevice)))

        return self.__sendModemCommand('63', binascii.unhexlify(self.__getX10CommandCommand(destinationDevice, commandId1)))


    #low level processing methods
    def __process_PLMInfo(self, responseBytes):
        (modemCommand, idHigh, idMid, idLow, deviceCat, deviceSubCat, firmwareVer, acknak) = struct.unpack('xBBBBBBBB', responseBytes)

        foundCommandHash = None
        #find our pending command in the list so we can say that we're done (if we are running in syncronous mode - if not well then the caller didn't care)
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
            if binascii.unhexlify(commandDetails['modemCommand']) == chr(modemCommand):
                #Looks like this is our command.  Lets deal with it
                self._commandReturnData[commandHash] = { 'id': _byteIdToStringId(idHigh,idMid,idLow), 'deviceCategory': '%02X' % deviceCat, 'deviceSubCategory': '%02X' % deviceSubCat, 'firmwareVersion': '%02X' % firmwareVer }    

                waitEvent = commandDetails['waitEvent']
                waitEvent.set()

                foundCommandHash = commandHash
                break

        if foundCommandHash:
            del self._pendingCommandDetails[foundCommandHash]
        else:
            print "Unable to find pending command details for the following packet:"
            print hex_dump(responseBytes, len(responseBytes))

    def __process_StandardInsteonMessagePLMEcho(self, responseBytes):
        #print utilities.hex_dump(responseBytes, len(responseBytes))
        #we don't do anything here.  Just eat the echoed bytes
        pass

    def __process_StandardX10MessagePLMEcho(self, responseBytes):
        # Just ack / error echo from sending an X10 command
        pass

    def __validResponseMessagesForCommandId(self, commandId):
        if self.__insteonCommands.has_key(commandId):
            commandInfo = self.__insteonCommands[commandId]
            if commandInfo.has_key('validResponseCommands'):
                return commandInfo['validResponseCommands']

        return False

    def __process_InboundStandardInsteonMessage(self, responseBytes):
        (insteonCommand, fromIdHigh, fromIdMid, fromIdLow, toIdHigh, toIdMid, toIdLow, messageFlags, command1, command2) = struct.unpack('xBBBBBBBBBB', responseBytes)        

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
        for (commandHash, commandDetails) in self.__pendingCommandDetails.items():

            #since this was a standard insteon message the modem command used to send it was a 0x62 so we check for that
            if binascii.unhexlify(commandDetails['modemCommand']) == '\x62':
                originatingCommandId1 = None
                if commandDetails.has_key('commandId1'):
                    originatingCommandId1 = commandDetails['commandId1']
                    
                validResponseMessages = self.__validResponseMessagesForCommandId(originatingCommandId1)
                if validResponseMessages and len(validResponseMessages):
                    #Check to see if this received command is one that this pending command is waiting for
                    if validResponseMessages.count(insteonCommandCode) == 0:
                        #this pending command isn't waiting for a response with this command code...  Move along
                        continue
                else:
                    print "Unable to find a list of valid response messages for command %s" % originatingCommandId1
                    continue
                        
                    
                #since there could be multiple insteon messages flying out over the wire, check to see if this one is from the device we send this command to
                destDeviceId = None
                if commandDetails.has_key('destinationDevice'):
                    destDeviceId = commandDetails['destinationDevice']
                        
                if destDeviceId:
                    if destDeviceId == _byteIdToStringId(fromIdHigh, fromIdMid, fromIdLow):
                                                                        
                        returnData = {} #{'isBroadcast': isBroadcast, 'isDirect': isDirect, 'isAck': isAck}
                        
                        #try and look up a handler for this command code
                        if self.__insteonCommands.has_key(insteonCommandCode):
                            if self.__insteonCommands[insteonCommandCode].has_key('callBack'):
                                (requestCycleDone, extraReturnData) = self.__insteonCommands[insteonCommandCode]['callBack'](responseBytes)
                                                        
                                if extraReturnData:
                                    returnData = dict(returnData.items() + extraReturnData.items())
                                
                                if requestCycleDone:                                    
                                    waitEvent = commandDetails['waitEvent']                                    
                            else:
                                print "No callBack for insteon command code %s" % insteonCommandCode    
                        else:
                            print "No insteonCommand lookup defined for insteon command code %s" % insteonCommandCode    
                                
                        if len(returnData):
                            self.__commandReturnData[commandHash] = returnData
                                                                                                                
                        foundCommandHash = commandHash
                        break
            
        if foundCommandHash == None:
            print "Unhandled packet (couldn't find any pending command to deal with it)"
            print "This could be an unsolocicited broadcast message"
                        
        if waitEvent and foundCommandHash:
            waitEvent.set()            
            del self.__pendingCommandDetails[foundCommandHash]
            
            print "Command %s completed" % foundCommandHash
    
    def __process_InboundExtendedInsteonMessage(self, responseBytes):
        #51 
        #17 C4 4A     from
        #18 BA 62     to
        #50         flags
        #FF         cmd1
        #C0         cmd2
        #02 90 00 00 00 00 00 00 00 00 00 00 00 00    data
        (insteonCommand, fromIdHigh, fromIdMid, fromIdLow, toIdHigh, toIdMid, toIdLow, messageFlags, command1, command2, data) = struct.unpack('xBBBBBBBBBB14s', responseBytes)        
        
        pass
        
    def __process_InboundX10Message(self, responseBytes):        
        "Receive Handler for X10 Data"
        #X10 sends commands fully in two separate messages. Not sure how to handle this yet
        #TODO not implemented
        unitCode = None
        commandCode = None
        print "X10> ", hex_dump(responseBytes, len(responseBytes)),
 #       (insteonCommand, fromIdHigh, fromIdMid, fromIdLow, toIdHigh, toIdMid, toIdLow, messageFlags, command1, command2) = struct.unpack('xBBBBBBBBBB', responseBytes)        
#        houseCode =     (int(responseBytes[4:6],16) & 0b11110000) >> 4 
 #       houseCodeDec = X10_House_Codes.get_key(houseCode)
#        keyCode =       (int(responseBytes[4:6],16) & 0b00001111)
#        flag =          int(responseBytes[6:8],16)
        
        
                
    #insteon message handlers
    def __handle_StandardDirect_IgnoreAck(self, messageBytes):
        #just ignore the ack for what ever command triggered us
        #there is most likley more data coming for what ever command we are handling
        return (False, None)
        
    def __handle_StandardDirect_AckCompletesCommand(self, messageBytes):
        #the ack for our command completes things.  So let the system know so
        return (True, None)                            
                                                    
    def __handle_StandardBroadcast_SetButtonPressed(self, messageBytes):
        #02 50 17 C4 4A 01 19 38 8B 01 00
        (idHigh, idMid, idLow, deviceCat, deviceSubCat, deviceRevision) = struct.unpack('xxBBBBBBxxx', messageBytes)
        return (True, {'deviceType': '%02X%02X' % (deviceCat, deviceSubCat), 'deviceRevision':'%02X' % deviceRevision})

    def __handle_StandardDirect_EngineResponse(self, messageBytes):
        #02 50 17 C4 4A 18 BA 62 2B 0D 01
        engineVersionIdentifier = messageBytes[10]
        return (True, {'engineVersion': engineVersionIdentifier == '\x01' and 'i2' or 'i1'})

    def __handle_StandardDirect_LightStatusResponse(self, messageBytes):
        #02 50 17 C4 4A 18 BA 62 2B 00 00
        lightLevelRaw = messageBytes[10]

        #map the lightLevelRaw value to a sane value between 0 and 1
        normalizedLightLevel = simpleMap(ord(lightLevelRaw), 0, 255, 0, 1)

        return (True, {'lightStatus': round(normalizedLightLevel, 2) })

    #public methods        
    def getPLMInfo(self, timeout = None):        
        commandExecutionDetails = self.__sendModemCommand('60')
            
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)                            
            
    def pingDevice(self, deviceId, timeout = None):        
        startTime = time.time()
        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '0F', '00')                

        #Wait for ping result
        commandReturnCode = self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)    
        endTime = time.time()
        
        if commandReturnCode:
            return endTime - startTime
        else:
            return False
            
    def idRequest(self, deviceId, timeout = None):                
        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '10', '00')                        
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)    
        
    def getInsteonEngineVersion(self, deviceId, timeout = None):                
        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '0D', '00')                        
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)    
    
    def getProductData(self, deviceId, timeout = None):                
        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '03', '00')                        
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)    
            
    def lightStatusRequest(self, deviceId, timeout = None):                
        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '19', '00')                        
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)        
                    
    def command(self, device, command, timeout = None):
        command = command.lower()
        if isinstance(device, InsteonDevice):
            print "InsteonA"
            commandExecutionDetails = self.__sendStandardP2PInsteonCommand(device.deviceId, "%02x" % (HACommand()[command]['primary']['insteon']), "%02x" % (HACommand()[command]['secondary']['insteon']))
        elif isinstance(device, X10Device):
            print "X10A"
            commandExecutionDetails = self.__sendStandardP2PX10Command(device.deviceId,"%02x" % (HACommand()[command]['primary']['x10']))
        else:
            print "stuffing"
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)            
        
    def onCommand(self,callback):
        pass
    
    def turnOn(self, deviceId, timeout = None):        
        if len(deviceId) != 2: #insteon device address
            commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '11', 'ff')                        
        else: #X10 device address
            commandExecutionDetails = self.__sendStandardP2PX10Command(deviceId,'02')
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)            

    def turnOff(self, deviceId, timeout = None):
        if len(deviceId) != 2: #insteon device address
            commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '13', '00')
        else: #X10 device address
            commandExecutionDetails = self.__sendStandardP2PX10Command(deviceId,'03')
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)
    
    def turnOnFast(self, deviceId, timeout = None):        
        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '12', 'ff')
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    def turnOffFast(self, deviceId, timeout = None):
        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '14', '00')
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    def dimTo(self, deviceId, level, timeout = None):

        #organize what dim level we are heading to (figgure out the byte we need to send)
        lightLevelByte = simpleMap(level, 0, 1, 0, 255)

        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '11', '%02x' % lightLevelByte)
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    def brightenOneStep(self, deviceId, timeout = None):
        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '15', '00')
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)

    def dimOneStep(self, deviceId, timeout = None):
        commandExecutionDetails = self.__sendStandardP2PInsteonCommand(deviceId, '16', '00')
        return self.__waitForCommandToFinish(commandExecutionDetails, timeout = timeout)


######################
# EXAMPLE            #
######################


def __x10_received(houseCode, unitCode, commandCode):
    print 'X10 Received: %s%s->%s' % (houseCode, unitCode, commandCode)


def __insteon_received(*params):
    print 'InsteonPLM Received:', params

if __name__ == "__main__":

    #Lets get this party started
    insteonPLM = InsteonPLM(TCP('192.168.13.146', 9761))
#    insteonPLM = InsteonPLM(Serial('/dev/ttyMI0'))

    jlight = InsteonDevice('19.05.7b', insteonPLM)
    jRelay = X10Device('m1', insteonPLM)

    insteonPLM.start()

    jlight.set('faston')
    jlight.set('fastoff')
    jRelay.set('on')
    jRelay.set('off')

    # Need to get a callback implemented
    #    insteon.onReceivedInsteon(insteon_received)

    #sit and spin, let the magic happen
    select.select([], [], [])
