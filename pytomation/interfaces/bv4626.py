"""
File:
        bv4626.py

Description:

This is a driver for the ByVac 4626 board.  The BV4626 board is a digital I/O
board that has 8 I/O channels, named A to H, two relays, a DAC and an ADC.

The serial parameters for communications between the interface and PC
are as follows:

    Baud Rate:    115200
    RTSCTS:       True

Author(s):
         Colin Guthrie <colin@mageia.org>
         Copyright (c), 2013

         Based on the CM11A interface written by:
         George Farris <farrisg@gmsys.com>
         Copyright (c), 2012

         Functions common to Pytomation written by:
         Jason Sharpee <jason@sharpee.com>

License:
    This free software is licensed under the terms of the GNU public license, Version 3

Usage:

    see /example_bv4626_use.py

Notes:
    For documentation on the BV4626 please see:
    http://doc.byvac.com/index.php5?title=Product_BV4626

Versions and changes:
    Initial version created May 2014

    
"""
import time
import re

from .common import *
from maplinwirelesssocket import MaplinWirelessSocket
from .ha_interface import HAInterface

class Bv4626(HAInterface):
    VERSION = '1.0'
    
    _connected = False
    _outputs = ''
    _sockets = ''
    _validAddresses = False
    CR = '\015'
    ESC = '\033'
    ACK = '\006'

    def __init__(self, interface, *args, **kwargs):
        super(Bv4626, self).__init__(interface, *args, **kwargs)
        
    def _init(self, *args, **kwargs):
        super(Bv4626, self)._init(*args, **kwargs)

        self.version()
    
        self._modemCommands = {
          'getDeviceId': '?31d',
          'getFirmwareVersion': '?31f',
          'turnOn': '1',
          'turnOff': '0',
        }

        outputs_regexp = 'AB'
        valid_outputs = re.compile('a?b?c?d?e?f?g?h?')
        if 'outputs' in kwargs:
            self._logger.debug("Found Outputs: " + kwargs['outputs'])
            if valid_outputs.match(kwargs['outputs']):
                self._outputs = kwargs['outputs']
                outputs_regexp += kwargs['outputs']

        outputs_regexp = '[' + outputs_regexp + ']'

        if 'sockets' in kwargs:
            self._logger.debug("Found Maplin Sockets: " + kwargs['sockets'])
            if valid_outputs.match(kwargs['sockets']):
                no_overlap = True
                for c in kwargs['sockets']:
                    if self._outputs.find(c) != -1:
                        self._logger.error("Found overlapping output and socket " + c)
                        no_overlap = False
                if no_overlap:
                    self._sockets = kwargs['sockets']
                    self._outputs += self._sockets
                    outputs_regexp = '(' + outputs_regexp + ')|([' + self._sockets + '][1-4][1-4])'

        self._logger.debug('Valid outputs regex: ' + outputs_regexp)
        self._validAddresses = re.compile('^(' + outputs_regexp + ')$')

    def shutdown(self):
        super(Bv4626, self).shutdown()
        self._logger.debug("Shutting down")
        if self._connected:
            self._interface.close()
        
    def _connect(self):
        if self._connected:
            return True

        self._interface.write(self.CR) # establish Baud rate

        ack = False
        loop = 0
        while True:
            if self._interface.inWaiting() == 0:
                time.sleep(0.1)
                loop += 1
                if loop > 30:
                    self._logger.debug("Error connecting to device.")
                    return False
                continue

            ack = self._interface.read(1)
            if ack == '*':
                self._logger.debug("Got connection marker. Clearing buffers and setting ACK")
                break
            elif ack:
                self._logger.debug("Read something odd during connection: '" + ack + "'")
        
        # requires text to be sent
        self._interface.write('Clearing buffer\r') # clears buffer
        self._interface.write('\r')
        self._interface.write(self.ESC+'['+str(ord(self.ACK))+'E') # set ACK
        self._connected = True

        rv = True
        if self._outputs:
            val = 0
            for c in 'abcdefgh':
                if c not in self._outputs:
                    pin = ord(c) - 97 # a = 0, b = 1...
                    val += 2**pin
            self._logger.debug("Setting output pins " + self._outputs +  " (" + str(val) + ")")
            if self._sendInterfaceCommand(str(val)+'s'):
                self._logger.debug("Output pins configured.")
            else:
                self._logger.debug("Output pins NOT configured.")
                rv = False

        return rv

    def _readInterface(self, lasPacketHash):
        #self._connect()
        time.sleep(0.5)


    def _sendInterfaceCommand(self, command, expectsReply=False):
        if not self._connect():
            return False

        self._logger.debug("Sending command: '" + command + "'")
        self._interface.write(self.ESC + '[' + command)

        buffer = ''
        c = ''
        ack = False
        loop = 0
        while True:
            if self._interface.inWaiting() == 0:
                time.sleep(0.1)
                loop += 1
                if loop > 30:
                    self._logger.debug("Error waiting for response from interface, giving up...")
                    return False
                continue

            ack = self._interface.read(1)
            if ack == self.ACK:
                self._logger.debug("Got ACK (after " + str(len(buffer)) + " bytes of data)")
                break
            if ack:
                #self._logger.debug("Got data")
                buffer += ack

        if expectsReply and not buffer:
            self._logger.debug("Did not get a reply when one was expected :s")
        
        if expectsReply:
            return buffer

        return True
        
    def getDeviceId(self):
        return self._sendInterfaceCommand(self._modemCommands['getDeviceId'], True)

    def getFirmwareVersion(self):
        return self._sendInterfaceCommand(self._modemCommands['getFirmwareVersion'], True)

    def _maplinSwitch(self, address, channel, button, on=True):
        if not self._connect():
            return False
        self._logger.debug('Sending ' + ('ON' if on else 'OFF') + ' to address> ' + address + ' (via Maplin Wireless Socket ' + str(button) + ' on channel ' + str(channel) + ')')
        self._logger.debug('Clearing ACK')
        self._interface.write(self.ESC+'[0E') # Clear ACK
        socket = MaplinWirelessSocket(lambda: self._interface.write(self.ESC+'[255'+address), lambda: self._interface.write(self.ESC+'[0'+address))
        self._logger.debug('Sending signal...')
        if on:
            socket.on(channel, button)
        else:
            socket.off(channel, button)
        self._logger.debug('Resetting ACK')
        self._interface.write(self.ESC+'['+str(ord(self.ACK))+'E') # set ACK
        return True

    def on(self, address):
        if not self._validAddresses.match(address):
            self._logger.error("Invalid address '" + address + "'")
            return False

        if len(address) > 1:
            pin = address[0]
            channel = int(address[1])
            button = int(address[2])
            return self._maplinSwitch(pin, channel, button)

        self._logger.debug("Sending ON to address> " + address)
        if address == address.upper():
          return self._sendInterfaceCommand(self._modemCommands['turnOn'] + address)

        return self._sendInterfaceCommand('255' + address)
            
    def off(self, address):
        if not self._validAddresses.match(address):
            self._logger.error("Invalid address '" + address + "'")
            return False

        if len(address) > 1:
            pin = address[0]
            channel = int(address[1])
            button = int(address[2])
            return self._maplinSwitch(pin, channel, button, False)

        self._logger.debug("Sending OFF to address> " + address)
        if address == address.upper():
          return self._sendInterfaceCommand(self._modemCommands['turnOff'] + address)

        return self._sendInterfaceCommand('0' + address)

    def version(self):
        self._logger.info("Bv4626 Pytomation driver version " + self.VERSION)
