from .ha_interface import HAInterface
#from .common import Interface
from pytomation.devices import State

import subprocess
import time

class Arp(HAInterface):
	VERSION = '0.0.1'

	def __init__(self):
		super(Arp, self).__init__(self)
		pass

	def _readInterface(self, lastPacketHash):
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
				arping = None
				try:
					subprocess.check_output(["arping","-c 1",address])
					arping = True
					self._onState(state=State.ON, address=hwaddress)
				except:
					#print ["arping","-c 1",address]
					arping = False
					self._onState(state=State.OFF, address=hwaddress)
		#print "waiting"
		time.sleep(5)
