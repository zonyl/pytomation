"""
File:
        wtdio.py

Description:

This is a driver for the Weeder WTDIO board.  The WDTIO board is a digital I/O 
board that has 14 I/O channel on it, named A to N.  The Weeder boards can be 
daisy chanined up to 16 boards.  Each board has DIP switch settings for it's 
address and are defined as A to P.

This driver will re-initialize any of the boards that experience a power on 
reset or brownout without having to restart Pytomation.

The the I/O channels on the WTDIO board are set according to the following 
command set.
S = Switch, L = Output, default low

Inputs are set by sending the board data in the following sequence.  
BOARD TYPE CHANNEL
Example:  Board 'A', Type SWITCH, Channel D - 'ASD'
Currently only SWITCH inputs are handled.

Outputs are set as follows: BOARD LEVEL CHANNEL
Example:  Board 'A', Level LOW, Channel 'M', - 'ALM'

It's possible to set the output to a HIGH level when it is initialized but 
this is not supported by this driver.

I'll change this later to make full use of the weeder boards capabilities


Author(s):
         George Farris <farrisg@gmsys.com>
         Copyright (c), 2012

         Functions common to Pytomation written by:
         Jason Sharpee <jason@sharpee.com> 

License:
    This free software is licensed under the terms of the GNU public license, Version 3

Usage:

    see /example_wtdio_use.py

Notes:
    For documentation on the Weeder wtdio please see:
    http://www.weedtech.com/wtdio-m.html

    This driver only supports 16 boards at present A-P

Versions and changes:
    Initial version created on Sept 10 , 2012
    2012/10/20 - 1.1 - Added version number and acknowledgement of Jasons work
                     - Added debug to control printing results
    2012/11/10 - 1.2 - Added debug levels and global debug system
    2012/11/18 - 1.3 - Added logging 
    2012/11/30 - 1.4 - Unify Command and State magic strings
    2012/12/07 - 1.5 - Add invert pin function.
    2012/12/07 - 1.6 - Update to new logging stuff
    2012/12/17 - 1.7 - readModem command now readInterface
    2013/02/15 - 1.8 - Fix output to channel
    
"""
import threading
import time
import re
from Queue import Queue
from binascii import unhexlify

from .common import *
from .ha_interface import HAInterface


class Wtdio(HAInterface):
    VERSION = '1.8'
        
    def __init__(self, interface, *args, **kwargs):
        super(Wtdio, self).__init__(interface, *args, **kwargs)
        
    def _init(self, *args, **kwargs):
        super(Wtdio, self)._init(*args, **kwargs)

        self.version()
        self.boardSettings = []
        self._modemRegisters = ""

        self._modemCommands = {
                               }

        self._modemResponse = {
                               }
        # for inverting the I/O point 
        self.d_inverted = [False for x in xrange(14)]
                
        self.echoMode()	 #set echo off

        		
    def _readInterface(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read()
        if len(responses) != 0:
            for response in responses.split():
                self._logger.debug("[WTDIO] Response> " + hex_dump(response))
                p = re.compile('[A-P][A-N][H,L]')
                if p.match(response):
                    self._processDigitalInput(response, lastPacketHash)
                elif response[1] =='!':
                    self._logger.debug("[WTDIO] Board [" + response[0] + "] has been reset or power cycled, reinitializing...\n")
                    for bct in self.boardSettings:
                        if bct[0] == response[0]:
                            self.setChannel(bct)
                elif response[1] == '?':
                    self._logger.debug("[WTDIO] Board [" + response[0] + "] received invalid command or variable...\n")
                    
        else:
            #print "Sleeping"
            #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
            #time.sleep(0.1)
            time.sleep(0.5)

    # response[0] = board, resonse[1] = channel, response[2] = L or H    
    def _processDigitalInput(self, response, lastPacketHash):
        if (response[2] == 'L' and not self.d_inverted[ord(response[1]) - 65]):
        #if (response[2] == 'L'):
            contact = Command.OFF
        else:
            contact = Command.ON
        self._onCommand(address=response[:2],command=contact)


    def _processNewWTDIO(self, response):
        pass

	# Turn echo mode off on Weeder board
    def echoMode(self, timeout=None):
        command = 'AX0\r'
        commandExecutionDetails = self._sendInterfaceCommand(
                             command)

    # Initialize the Weeder board, input example "ASA"
    def setChannel(self, boardChannelType):
        p = re.compile('[A-P][S,L][A-N]')
        if not p.match(boardChannelType):
            self._logger.debug("[WTDIO] Error malformed command...   " + boardChannelType + '\n')
            return
        # Save the board settings in case we need to re-init
        if not boardChannelType in self.boardSettings:
            self.boardSettings.append(boardChannelType)
                
        command = boardChannelType + '\r'
        commandExecutionDetails = self._sendInterfaceCommand(command)

    def dio_invert(self, channel, value=True):
        self.d_inverted[ord(channel) - 65] = value
                    
    def on(self, address):
        command = address[0] + 'H' + address[1] + '\r'
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)

    def off(self, address):
        command = address[0] + 'L' + address[1] + '\r'
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)
		
    def listBoards(self):
        self._logger.info(self.boardSettings + '\n')
        
    def version(self):
        self._logger.info("WTDIO Pytomation driver version " + self.VERSION + '\n')

