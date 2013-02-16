"""
File: 
    arduino_uno.py

George Farris <farrisg@gmsys.com>
Copyright (c), 2013

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.



Description:

This is a driver for the Arduino UNO board used with the included uno.pde 
sketch.  The UNO board supports digital and analog I/O.  The Uno board can be 
configured to use up 18 digital I/O channels or 12 digital and 6 analog 
channels or a combination of both.

This driver will re-initialize any of the boards that experience a power on 
reset or brownout without having to restart Pytomation.

The the I/O channels on the Andunio board are set according to the following 
command set.

Every command sent to the board is three or four characters in length.  There 
is no terminating CR or NL character.

  [Board] [I/O direction] [Pin]
  ===========================================================================
  [Board] 	- 'A'
  [I/O]		- 'DN<pin>' Configure as Digital Input no internal pullup (default)
  			- 'DI<pin>'     "      " Digital Input uses internal pullup
	  		- 'DO<pin>'     "      " Digital Output 
	  		- 'AI<pin>'     "      " Analog Input
			- 'AO<pin>'     "      " Analog Output
	        - 'L<pin>'  Set Digital Output to LOW
	        - 'H<pin>'  Set Digital Output to HIGH
			- '%<pin><value>'  Set Analog Output to value (0 - 255)
  [Pin]		- Ascii 'C' to 'T'  C = pin 2, R = pin A3, etc
 
  Examples transmitted to board:
    ADIF	Configure pin 5 as digital input with pullup
	AAIR	Configure pin A3 as analog input
	AHE		Set digital pin 4 HIGH
	A%D75	Set analog output to value of 75

  Examples received from board:  NOTE the end of message (eom) char '.'
	AHE.		Digital pin 4 is HIGH
	ALE.		Digital pin 4 is LOW
	AP89.		Analog pin A1 has value 89
	
  Available pins, pins with ~ can be analog Output
                  pins starting with A can be Analog Inut
                  All pins can be digital except 0 and 1
  ----------------------------------------------------------------------------
  02 03 04 05 06 07 08 09 10 11 12 13 A0 A1 A2 A3 A4 A5
  C  D  E  F  G  H  I  J  K  L  M  N  O  P  Q  R  S  T
     ~     ~  ~        ~  ~  ~
  ============================================================================ 
  The board will return a '?' on error.
  The board will retunr a '!' on power up or reset.


Author(s):
         George Farris <farrisg@gmsys.com>
         Copyright (c), 2013


License:
    This free software is licensed under the terms of the GNU public license, 
    Version 3

Usage:

    see /example_Arduino_use.py

Notes:
    For documentation on the Ardunio Uno please see:
    http://arduino.cc/en/Main/arduinoBoardUno

    This driver only supports 1 board at present.

Versions and changes:
    Initial version created on Feb 14, 2013
    2013/02/14 - 1.0 - Initial version
    
"""
import threading
import time
import re
from Queue import Queue
from binascii import unhexlify

from .common import *
from .ha_interface import HAInterface


class Arduino(HAInterface):
    VERSION = '1.0'
    MODEM_PREFIX = ''
    
    
    def __init__(self, interface, *args, **kwargs):
        super(Arduino, self).__init__(interface, *args, **kwargs)
        
    def _init(self, *args, **kwargs):
        super(Arduino, self)._init(*args, **kwargs)

        self.version()
        self.boardSettings = []
        self._modemRegisters = ""

        self._modemCommands = {
                               }

        self._modemResponse = {
                               }
        # for inverting the I/O point 
        self.d_inverted = [False for x in xrange(19)]
        #self._interface.read(100)        
        		
    def _readInterface(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read()
        if len(responses) != 0:
            for response in responses.split():
                self._logger.debug("[Arduino] Response> " + hex_dump(response))
                d = re.compile('[A][C-T][H,L][\.]')
                a = re.compile('[A][O-T][0-9]*[\.]')    
                if d.match(response):
                    # strip end of message :a.index('.')
                    self._processDigitalInput(response[:response.index('.')], lastPacketHash)
                elif a.match(response):
                    self._processAnalogInput(response[:response.index('.')], lastPacketHash)
                elif response[1] == '!':
                    self._logger.debug("[Arduino] Board [" + response[0] + "] has been reset or power cycled, reinitializing...\n")
                    #while self._interface.read():
                    pass
                    #for bct in self.boardSettings:
                    #    if bct[0] == response[0]:
                    #        self.setChannel(bct)
                elif response[1] == '?':
                    self._logger.debug("[Arduino] Board [" + response[0] + "] received invalid command or variable...\n")
                    
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
            self._logger.debug("[Arduino] Unable to find pending command details for the following packet:\n")
            self._logger.debug((hex_dump(response, len(response)) + '\n'))


    # Initialize the Uno board, input example "ADIC"
    def setChannel(self, boardChannelType):
        p = re.compile('[A][A,D][I,N,O][C-T]')
        if not p.match(boardChannelType):
            self._logger.debug("[Arduino] Error malformed command...   " + boardChannelType + '\n')
            return
        # Save the board settings in case we need to re-init
        #if not boardChannelType in self.boardSettings:
        #    self.boardSettings.append(boardChannelType)
                
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

		
    def listBoards(self):
        self._logger.info(self.boardSettings + '\n')
        
    def version(self):
        self._logger.info("Ardunio Pytomation driver version " + self.VERSION + '\n')

