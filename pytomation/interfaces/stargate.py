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
    2012/11/30 - 1.3 - Unify Command and State magic strings across the system
    2012/12/09 - 1.4 - Bump version number
"""
import threading
import time
from Queue import Queue
from binascii import unhexlify

from .common import *
from .ha_interface import HAInterface

class Stargate(HAInterface):
    VERSION = '1.4'

    def __init__(self, interface, *args, **kwargs):
        super(Stargate, self).__init__(interface, *args, **kwargs)

    def _init(self, *args, **kwargs):
        super(Stargate, self)._init(*args, **kwargs)

        self.version()
        
        self._last_input_map_low = None
        self._last_input_map_high = None

        self._modemRegisters = ""

        self._modemCommands = {

                               }

        self._modemResponse = {
                               }
        self.d_inverted = [False for x in xrange(16)]
        self.echoMode()
	self._logger.error('Startgggg')

    def _readInterface(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read()
        if len(responses) != 0:
            for response in responses.split():
                self._logger.debug("Response>" + hex_dump(response))
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
        first_time = False
        if self._last_input_map_low == None: #First Time
            self._last_input_map_high = 0
            self._last_input_map_low = 0
            first_time = True

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
        

        for i in xrange(8):
            i_value = io_map & (2 ** i)
            i_prev_value = last_input_map & (2 ** i)
            if i_value != i_prev_value or first_time:
                if (not bool(i_value == 0) and not self.d_inverted[i]) or (bool(i_value == 0) and self.d_inverted[i]):
                    state = Command.ON
                else:
                    state = Command.OFF
		self._logger.info("Digital Input #{input} to state {state}".format(
				input=str(offset + i + 1),
				state=state))
                self._onCommand(command=state,
                                address='D' + str(offset + i + 1))

        if range == 'c': # High side of 16bit registers
            self._last_input_map_high = io_map
        else:
            self._last_input_map_low = io_map
	
        self._logger.debug("Process digital input {iomap} {offset} {last_inputl} {last_inputh}".format(
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

    def echoMode(self, timeout=None):
        command = '##%1d\r'
        commandExecutionDetails = self._sendInterfaceCommand(
                             command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    def dio_invert(self, channel, value=True):
        self.d_inverted[channel-1] = value

    def version(self):
        self._logger.info("Stargate Pytomation driver version " + self.VERSION)
