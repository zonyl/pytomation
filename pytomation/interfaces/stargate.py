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

Versions and changes:
    Initial version created on May 06 , 2011
    2012/11/14 - 1.1 - Added debug levels and global debug system
    2012/11/19 - 1.2 - Added logging, use pylog instead of print
    
"""
import threading
import time
from Queue import Queue
from binascii import unhexlify

from .common import *
from ..devices import State
from .ha_interface import HAInterface
from ..config import *

class Stargate(HAInterface):
#    MODEM_PREFIX = '\x12'
    MODEM_PREFIX = ''
    VERSION = '1.2'

    def __init__(self, interface):
        super(Stargate, self).__init__(interface)

    def _init(self, *args, **kwargs):
        super(Stargate, self)._init(*args, **kwargs)

        if not debug.has_key('Stargate'):
            debug['Stargate'] = 0
        self.version()
        
        self._last_input_map_low = 0
        self._last_input_map_high = 0

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
            for response in responses.split():
                if debug['Stargate'] > 0:
                    pylog("[Stargate] Response>\n" + hex_dump(response) + "\n")
                if response[:2] == "!!":  # Echo Mode activity -- !!mm/ddttttttjklm[cr]
                    if self._decode_echo_mode_activity(response)['j'] == 'a' or \
                        self._decode_echo_mode_activity(response)['j'] == 'c':
                        self._processDigitalInput(response, lastPacketHash)
        else:
            #print "Sleeping"
            #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
            #time.sleep(0.1)
            time.sleep(0.5)

    def _processDigitalInput(self, response, lastPacketHash):
        offset = 0
        last_input_map = self._last_input_map_low

        if response[-1] == 'f':
            a=1
        range = self._decode_echo_mode_activity(response)['j']
        io_map = Conversions.ascii_to_int( Conversions.hex_to_ascii(
                self._decode_echo_mode_activity(response)['l'] + \
                self._decode_echo_mode_activity(response)['m']
                ))

        if range == 'c': # High side of 16bit registers
            offset = 8
            last_input_map = self._last_input_map_high 
        

        for i in xrange(7):
            if last_input_map & (2 ** i) != io_map & (2 ** i):
                if not bool(io_map & (2 ** i) == 0):
                    state = State.ON
                else:
                    state = State.OFF
                self._onCommand(command=state,
                                address='D' + str(offset + i + 1))

        if range == 'c': # High side of 16bit registers
            self._last_input_map_high = io_map
        else:
            self._last_input_map_low = io_map

        pylog(__name__, " Process digital input {iomap} {offset} {last_inputl} {last_inputh}".format(
                                             iomap=Conversions.int_to_hex(io_map),
                                             offset=offset,
                                             last_inputl=Conversions.int_to_hex(self._last_input_map_low),
                                             last_inputh=Conversions.int_to_hex(self._last_input_map_high),
                                                                             ))


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
            pylog("[Stargate] Unable to find pending command details for the following packet:\n")
            pylog(hex_dump(response, len(response)) + "\n")

    def _processNewUBP(self, response):
        pass

    def echoMode(self, timeout=None):
        command = '##%1d\r'
        commandExecutionDetails = self._sendModemCommand(
                             command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    def version(self):
        pylog(__name__, "Stargate Pytomation driver version " + self.VERSION + "\n")
