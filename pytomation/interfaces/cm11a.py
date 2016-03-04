"""
File: 
    cm11a.py

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

This is a driver for the X10 CM11a
The serial parameters for communications between the interface and PC
are as follows:

	Baud Rate:	4,800bps
	Parity:		None
	Data Bits:	8
	Stop Bits:	1

2.1 Cable connections:

        Signal  DB9 Connector   RJ11 Connector
        SIN     Pin 2           Pin 1
        SOUT    Pin 3           Pin 3
        GND     Pin 5           Pin 4
        RI      Pin 9           Pin 2

where:  SIN     Serial input to PC (output from the interface)
        SOUT    Serial output from PC (input to the interface)
        GND     Signal ground
        RI      Ring signal (input to PC)

The housecodes and device codes range from A to P and 1 to 16
respectively although they do not follow a binary sequence. The encoding
format for these codes is as follows

	Housecode	Device Code	Binary Value	Hex Value
	A		1		0110		6
	B		2		1110		E
	C		3		0010		2
	D		4		1010		A
	E		5		0001		1
	F		6		1001		9
	G		7		0101		5
	H		8		1101		D
	I		9		0111		7
	J		10		1111		F
	K		11		0011		3
	L		12		1011		B
	M		13		0000		0
	N		14		1000		8
	O		15		0100		4
	P		16		1100		C

1.2	Function Codes.

	Function			Binary Value	Hex Value
	All Units Off			0000		0
	All Lights On			0001		1
	On				0010		2
	Off				0011		3
	Dim				0100		4
	Bright				0101		5
	All Lights Off			0110		6
	Extended Code			0111		7
	Hail Request			1000		8
	Hail Acknowledge		1001		9
	Pre-set Dim (1)			1010		A
	Pre-set Dim (2)			1011		B
	Extended Data Transfer		1100		C
	Status On			1101		D
	Status Off			1110		E
	Status Request			1111		F

Here's a log of A1, A ON.

05/03/05 7:14:09 AM > [04 66]
05/03/05 7:14:09 AM < [6A]
05/03/05 7:14:09 AM > [00]
05/03/05 7:14:10 AM < [55]
05/03/05 7:14:10 AM > [0E 62]
05/03/05 7:14:10 AM < [70]
05/03/05 7:14:10 AM > [00]
05/03/05 7:14:10 AM < [55]

Author(s):
         George Farris <farrisg@gmsys.com>
         Copyright (c), 2013


License:
    This free software is licensed under the terms of the GNU public license, 
    Version 3

Usage:

    see /example_CM11a_use.py


Versions and changes:
    Initial version created on Mar 1, 2013
    2013/03/04 - 1.0 - Initial version
    
"""
import threading
import time
import re
from Queue import Queue
from binascii import unhexlify

from .common import *
from .ha_interface import HAInterface

def simpleMap(value, in_min, in_max, out_min, out_max):
    return ((float(value) - float(in_min)) * (float(out_max) - float(out_min)) / (float(in_max) - float(in_min)) + float(out_min))
    
class CM11a(HAInterface):
    VERSION = '1.0'
    
    def __init__(self, interface, *args, **kwargs):
        super(CM11a, self).__init__(interface, *args, **kwargs)
        
    def _init(self, *args, **kwargs):
        super(CM11a, self)._init(*args, **kwargs)

        self.version()
        self.ready = True   # if interface is ready to rx command
        self.chksum = 0	    # checksum for command
	
        self._houseCode = {
                'A':0x60, 'B':0xE0, 'C':0x20, 'D':0xA0, 'E':0x10,
                'F':0x90, 'G':0x50, 'H':0xD0, 'I':0x70, 'J':0xF0,
                'K':0x30, 'L':0xB0, 'M':0x00, 'N':0x80, 'O':0x40,
                'P':0xC0}
                            
        self._unitCode = {
                '1':0x06, '2':0x0E, '3':0x02, '4':0x0A, '5':0x01,
                '6':0x09, '7':0x05, '8':0x0D, '9':0x07, '10':0x0F,
                '11':0x03, '12':0x0B, '13':0x00, '14':0x08, '15':0x04,
                '16':0x0C}

    def _readInterface(self, lasPacketHash):
	time.sleep(0.5)
	
	
    def _sendInterfaceCommand(self, hCode, uCode, command, level=0x06,):
	chksum = 0
	byte0 = 0x04
	byte1 = hCode + uCode
	self._logger.debug("[CM11a] Transmit > {b0} {b1}".format(b0=hex(byte0), b1=hex(byte1)))
	while (chksum != ((byte0 + byte1) & 0xFF)):
	    self._interface.write(chr(byte0) + chr(byte1))
	    chksum = ord(self._interface.read(1))

	self._interface.write(chr(0))

	ready = 0
	loop = 0
	while (ready != 0x55):
	    if self._interface.inWaiting() == 0:
		time.sleep(0.1)
		loop += 1
		if loop > 30:
		    self._logger.debug("[CM11a] Error waiting for response from interface, giving up...")
		    break
	    	continue
	    ready = ord(self._interface.read(1))

	byte0 = level | 0x06
	byte1 =  hCode + command
	chksum = 0
	self._logger.debug("[CM11a] Transmit > {b0} {b1}".format(b0=hex(byte0), b1=hex(byte1)))
	while (chksum != ((byte0 + byte1) & 0xFF)):
	    self._interface.write(chr(byte0))
	    self._interface.write(chr(byte1))
	    chksum = ord(self._interface.read())

	self._interface.write(chr(0))

	ready = 0
	loop = 0
	while (ready != 0x55):
	    if self._interface.inWaiting() == 0:
		time.sleep(0.1)
		loop += 1
		if loop > 50:  # need longer delay here when dimming
		    self._logger.debug("[CM11a] Error waiting for response from interface, giving up...")
		    break
	    	continue
	    ready = ord(self._interface.read())
	
    def on(self, address):
	hc = self._houseCode[address[0]]
	uc = self._unitCode[address[1]]
	self._logger.debug("[CM11a] Sending ON to address> " + address)
	self._sendInterfaceCommand(hc, uc, 2)
	        
    def off(self, address):
	hc = self._houseCode[address[0]]
	uc = self._unitCode[address[1]]
	self._logger.debug("[CM11a] Sending OFF to address> " + address)
	self._sendInterfaceCommand(hc, uc, 3)

    def level(self, address, level, rate=None, timeout=None):
	hc = self._houseCode[address[0]]
	uc = self._unitCode[address[1]]
	self._logger.debug("[CM11a] Sending DIM to address> " + address)
	lv = int(simpleMap(level,1,100,248,8)) & 0xF8	# min and max out are reversed
	self._sendInterfaceCommand(hc, uc, 4, lv)

    def version(self):
        self._logger.info("CM11a Pytomation driver version " + self.VERSION + '\n')

