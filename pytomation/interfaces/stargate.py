"""
File:
        stargate.py

Description:


Author(s):
         Jason Sharpee <jason@sharpee.com>  http://www.sharpee.com

License:
    This free software is licensed under the terms of the GNU public license, Version 1

Usage:

    see /example_use.py

Example:
    see /example_use.py

Notes:
    Protocol
    http://www.jdstechnologies.com/protocol.html

    2400 Baudrate


Created on May , 2012
"""
import threading
import time
from Queue import Queue
from binascii import unhexlify

from .common import *
from .ha_interface import HAInterface


class Stargate(HAInterface):
#    MODEM_PREFIX = '\x12'
    MODEM_PREFIX = ''

    def __init__(self, interface):
        super(Stargate, self).__init__(interface)
        self._last_input_map = 0
        
        self._modemRegisters = ""
        
        self._modemCommands = {

                               }

        self._modemResponse = {
                               }

        self.echoMode()

    def _readModem(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read()
        if len(responses) != 0:
            print "Response>\n" + hex_dump(responses)
            if responses[:2] == "!!":  # Echo Mode activity -- !!mm/ddttttttjklm[cr]
                if self._decode_echo_mode_activity(responses)['j'] == 'a' or \
                    self._decode_echo_mode_activity(responses)['j'] == 'c':
                    self._processDigitalInput(responses, lastPacketHash)
        else:
            #print "Sleeping"
            #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
            #time.sleep(0.1)
            time.sleep(0.5)

    def _processDigitalInput(self, response, lastPacketHash):
        offset = 0
        range = self._decode_echo_mode_activity(response)['j']
        io_map = Conversions.ascii_to_int( Conversions.hex_to_ascii(
                self._decode_echo_mode_activity(response)['l'] + \
                self._decode_echo_mode_activity(response)['m']
                ))
        if range == 'c':
            offset = 8

        for i in xrange(7):
            if self._last_input_map & (2**i) != io_map & (2**i):
                self._onCommand(command=io_map & (2**i), address='D' + str(offset + i))

        self._last_input_map = io_map

    def _decode_echo_mode_activity(self, activity):
        decoded = {}
        decoded.update({'month': activity[2:4]})
        decoded.update({'day': activity[5:7]})
        decoded.update({'seconds': activity[7:13]})
        decoded.update({'j': activity[13]})
        decoded.update({'k': activity[14]})
        decoded.update({'l': activity[15]})
        decoded.update({'m': activity[16]})
        return decoded

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
            print "Unable to find pending command details for the following packet:"
            print hex_dump(response, len(response))

    def _processNewUBP(self, response):
        pass

    def echoMode(self, timeout=None):
        command = '##%1d\r'
        commandExecutionDetails = self._sendModemCommand(
                             command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)