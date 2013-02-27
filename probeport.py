#! /usr/bin/python

"""
 probeport.py
 Copyright (c) 2010 George Farris <farrisg@shaw.ca>	

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
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


Version history
  0.1  Jan 20, 2010 First release
  0.2  Feb 24, 2013 Change port names.
  0.3  Feb 26, 2013 Add Arduino Uno boards with Pytomation driver

USB serial port adapters have the annoying feature of changing every time 
Linux boots, probeport.py will query your devices and link them to the correct 
port.

probeport.py will probe all the ports in the SERIAL_PORTS list for any of the 
devices in the PROBE_DEVICES list.  Once a port is found it will be deleted 
from the SERIAL_PORTS so it won't continually be probed.

In your software  you should set the port devices accordingly, here is a sample
for Pytomation:

insteon = InsteonPLM(Serial('/dev/sp_insteon_plm', 19200, xonxoff=False))
wtdio = Wtdio(Serial('/dev/sp_weeder_wtdio', 9600))
w800 = W800rf32(Serial('/dev/sp_w800rf32', 4800, xonxoff=False))


This script should be run at boot time or any time before your software starts

If you have more or less than 4 ports you can add or subtract them to the 
SERIAL_PORTS list. Also, here is an example if you only have two devices such 
as a weeder board and a plm.

PROBE_DEVICES = ['probe_plm', 'probe_w800']
SERIAL_PORTS = ['/dev/ttyUSB0', '/dev/ttyUSB1']

Please feel free to forward other devices we can probe and I'll add them
to the list and release a new version.  Also please feel free to forward changes 
or bug fixes.  Thanks.  George farrisg@shaw.ca
"""


import sys, os, serial, string, binascii, time, tempfile

# -------------- User modifiable settings -----------------------------

#PROBE_DEVICES = ['test']
# make sure we probe the arduino first
PROBE_DEVICES = ['probe_plm', 'probe_wtdio', 'probe_w800', 'probe_uno']
SERIAL_PORTS = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyR1','/dev/ttyR2']
INSTEON_PLM_BAUD_RATE = 19200
WEEDER_IO_BAUD_RATE = 9600
WEEDER_BOARD_ADDRESS = "A"
W800RF32_BAUD_RATE = 4800
ARDUINO_UNO_BAUD_RATE = 9600
spports = []


# ------------- End of user modifiable settings -----------------------

def test():
	print "This is a test run...."


#-----------------------------------------------------------------------------
# Probe for the insteon serial PLM
# plm  send 0x02 0x73, receive 0x02 0x73 0xXX 0x00 0x00 0x06/0x15
#-----------------------------------------------------------------------------
def probe_plm():
	for myport in SERIAL_PORTS:
		print "Probing for Insteon PLM port -> " + myport
		
		try:
			id = SERIAL_PORTS.index(myport)
			ser = serial.Serial(myport, INSTEON_PLM_BAUD_RATE, timeout=2)
			# Probe for Insteon response to command		

			ser.write(binascii.a2b_hex("0273"))
			s2 = binascii.b2a_hex(ser.read(8))
			print s2
			if s2[0:4] == "0273":
				#print "linking " + myport + " to /dev/sp_insteon_plm"
				spports.append("linking " + myport + " to /dev/sp_insteon_plm")
				command = "/bin/ln -sf " + myport + " /dev/sp_insteon_plm"
				os.system(command)
				del SERIAL_PORTS[id]
				ser.close()
				break
			ser.close()

		except:
			print "Error - Could not open serial port..."

#-----------------------------------------------------------------------------
# Probe for the Weeder WTDIO-M 14 channel digital IO board
# weeder send A, receive A?
#-----------------------------------------------------------------------------
def probe_wtdio():
	for myport in SERIAL_PORTS:
		print "Probing for Weeder WTDIO-M IO board port -> " + myport
		
		try:
			id = SERIAL_PORTS.index(myport)
			ser = serial.Serial(myport, WEEDER_IO_BAUD_RATE, timeout=2)
			ser.write(WEEDER_BOARD_ADDRESS)
			s2 = ser.read(5)
			print s2
			if s2[0:2] == WEEDER_BOARD_ADDRESS + '?':
				spports.append("linking " + myport + " to /dev/sp_weeder_wtdio")
				command = "/bin/ln -sf " + myport + " /dev/sp_weeder_wtdio"
				os.system(command)
				del SERIAL_PORTS[id]
				ser.close()
				break
			ser.close()

		except:
			print "Error - Could not open serial port..."

#-----------------------------------------------------------------------------
# Probe for the W800RF32 x10 RF receiver
# w800   send 0xf0 0x29, receive 0x29
#-----------------------------------------------------------------------------
def probe_w800():
	for myport in SERIAL_PORTS:
		print "Probing for W800RF32 port -> " + myport
		
		try:
			id = SERIAL_PORTS.index(myport)
			ser = serial.Serial(myport, W800RF32_BAUD_RATE, timeout=2)
			ser.write(binascii.a2b_hex("F029"))
			s2 = binascii.b2a_hex(ser.read(8))
			print s2
			if s2[0:2] == "29":
				spports.append("linking " + myport + " to /dev/sp_w800rf32")
				command = "/bin/ln -sf " + myport + " /dev/sp_w800rf32"
				os.system(command)
				del SERIAL_PORTS[id]
				ser.close()
				break
			ser.close()

		except:
			print "Error - Could not open serial port..."

#-----------------------------------------------------------------------------
# Probe for the Arduino Uno with the Pytomation firmware
# uno   send '?', receive "PYARUNO <char>" where char is board address
#-----------------------------------------------------------------------------
def probe_uno():
	for myport in SERIAL_PORTS:
		print "Probing for Arduino Uno port -> " + myport
		
		try:
			id = SERIAL_PORTS.index(myport)
			ser = serial.Serial(myport, ARDUINO_UNO_BAUD_RATE, timeout=2)
			ser.write('?')
			ser.read(100)	#clear buffer
			ser.write('?')
			s2 = ser.read(9)
			print s2
			if s2[0:7] == "PYARUNO":
				spports.append("linking " + myport + " to /dev/sp_pyaruno")
				command = "/bin/ln -sf " + myport + " /dev/sp_pyaruno"
				os.system(command)
				del SERIAL_PORTS[id]
				ser.close()
				break
			ser.close()

		except:
			print "Error - Could not open serial port..."

def show():
	print '\n\n'
	print 'Report\n--------------------------------------------------'
	for line in spports:
		print line

if __name__ == "__main__":
	for device in PROBE_DEVICES:
		func = globals()[device]
		func()
	show ()


	print "Goodbye..."

