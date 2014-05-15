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
from .ha_interface import HAInterface

class Bv4626(HAInterface):
    VERSION = '1.0'
    
    _connected = False
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

    def shutdown(self):
        super(Bv4626, self).shutdown()
        self._logger.debug("Shutting down")
        if self._connected:
            self._interface.close()
        
    def _connect(self):
        if self._connected:
            return

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

    def _readInterface(self, lasPacketHash):
        #self._connect()
        time.sleep(0.5)


    def _sendInterfaceCommand(self, command, expectsReply=False):
        self._connect()
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

    def on(self, address):
        if address != 'A' and address != 'B':
            self._logger.debug("Invalid address '" + address + "'")
            return False
        self._logger.debug("Sending ON to address> " + address)
        return self._sendInterfaceCommand(self._modemCommands['turnOn'] + address)
            
    def off(self, address):
        if address != 'A' and address != 'B':
            self._logger.debug("Invalid address '" + address + "'")
            return False
        self._logger.debug("Sending OFF to address> " + address)
        return self._sendInterfaceCommand(self._modemCommands['turnOff'] + address)

    def version(self):
        self._logger.info("Bv4626 Pytomation driver version " + self.VERSION)
