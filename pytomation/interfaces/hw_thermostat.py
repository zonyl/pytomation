"""
Homewerks Radio Thermostat CT-30-H-K2 Wireless Thermostat with Wi-Fi Module, Dual Wireless Inputs and Touch Screen
http://www.amazon.com/gp/product/B004YZFU1Q/ref=oh_details_o01_s00_i00?ie=UTF8&psc=1

Protocol Docs:
http://radiothermostat.com/documents/RTCOA%20WiFI%20API%20V1_0R3.pdf

Essentially the Device is a simple REST interface. Kudos to them for making a straightforward and simple API!

Author(s):
Jason Sharpee
jason@sharpee.com

reuse from:
 George Farris <farrisg@gmsys.com>
"""
import json
import re
import time

from .ha_interface import HAInterface
from .common import *

class HW_Thermostat(HAInterface):
    
    def _readInterface(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read()
        if len(responses) != 0:
            for response in responses.split():
                self._logger.debug("[HW Thermostat] Response> " + hex_dump(response))
                d = re.compile('[A][C-T][H,L][\.]')
                a = re.compile('[A][O-T][0-9]*[\.]')    
                if d.match(response):
                    # strip end of message :a.index('.')
                    self._processDigitalInput(response[:response.index('.')], lastPacketHash)
                elif a.match(response):
                    self._processAnalogInput(response[:response.index('.')], lastPacketHash)
                elif response[0] == '!':
                    self._logger.debug("[HW Thermostat] Board [" + response[0] + "] has been reset or power cycled, reinitializing...\n")
                    for bct in self.boardSettings:
                        self.setChannel(bct)
                elif response[1] == '?':
                    self._logger.debug("[HW Thermostat] Board [" + response[0] + "] received invalid command or variable...\n")
                    
        else:
            time.sleep(0.1)  # try not to adjust this 

    # response[0] = board, response[1] = channel, response[2] = L or H    
    def _processDigitalInput(self, response, lastPacketHash):
        if (response[2] == 'L' and not self.d_inverted[ord(response[1]) - 65]):
        #if (response[2] == 'L'):
            contact = Command.OFF
        else:
            contact = Command.ON
        self._onCommand(address=response[:2],command=contact)

    # response[0] = board, response[1] = channel, response[2 to end] = value
    def _processAnalogInput(self, response, lastPacketHash):
        self._onCommand(address=response[:2],command=(Command.LEVEL, response[2:]))


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
            self._logger.debug("[HW Thermostat] Unable to find pending command details for the following packet:\n")
            self._logger.debug((hex_dump(response, len(response)) + '\n'))


    # Initialize the Uno board, input example "ADIC"
    def setChannel(self, boardChannelType):
        p = re.compile('[A][A,D][I,N,O][C-T]')
        if not p.match(boardChannelType):
            self._logger.debug("[HW Thermostat] Error malformed command...   " + boardChannelType + '\n')
            return
        # Save the board settings in case we need to re-init
        if not boardChannelType in self.boardSettings:
            self.boardSettings.append(boardChannelType)
        
        self._logger.debug("[HW Thermostat] Setting channel " + boardChannelType + '\n')
        command = boardChannelType
        commandExecutionDetails = self._sendInterfaceCommand(command)

    def dio_invert(self, channel, value=True):
        self.d_inverted[ord(channel) - 65] = value
                    
    def on(self, address):
        command = address[0] + 'H' + address[1]
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)

    def off(self, address):
        command = address[0] + 'L' + address[1]
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)

    def level(self, address, level, timeout=None, rate=None):
        command = address[0] + '%' + address[1] + level
        commandExecutionDetails = self._sendInterfaceCommand(command)

    def version(self):
        self._logger.info("HW Thermostat Pytomation driver version " + self.VERSION + '\n')