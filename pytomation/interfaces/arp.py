from .ha_interface import HAInterface
#from .common import Interface
from pytomation.devices import State
from .common import Command

import subprocess
import time


class Arp(HAInterface):
	VERSION = '0.0.1'

	_iteration = 0
	_poll_secs = 15
	rawdata = None
	arping = None

	def __init__(self):
		super(Arp, self).__init__(self)
		pass

	def _readInterface(self, lastPacketHash):

		if not self._iteration < self._poll_secs:
			self._iteration = 0
			rawdata = subprocess.check_output(["arp","-n"])
			data = rawdata.split('\n')

			addressstart = data[0].find('Address')   #[8][0:15].strip()
			hwaddressstart = data[0].find('HWaddress')

			#datadic = {}
		
			for line in data:
				address = line[addressstart:15].strip()
				hwaddress = line[hwaddressstart:(hwaddressstart + 18)].strip()
				if hwaddress != "(incomplete)" and hwaddress != "HWaddress" and hwaddress != "": 

					#datadic[hwaddress]=address
					try:
						arping = subprocess.check_output(["arping","-q","-c 1",address])
						arping = True
						#self._onState(state=State.ON, address=hwaddress)
						self._onCommand(command=Command.ON, address=hwaddress)
					except:
						#print ["arping","-c 1",address]
						arping = False
						#self._onState(state=State.OFF, address=hwaddress)
						self._onCommand(command=Command.OFF, address=hwaddress)
			#print "waiting"
		else:
			self._iteration += 1
			time.sleep(1)
