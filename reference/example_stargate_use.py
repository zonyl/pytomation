from pytomation.config import *
from pytomation.interfaces import Stargate, Serial


def on_digital_input(command=None, address=None):
    print "Digital Input #" + str(address) + " -> " + command

debug['Stargate'] = 1
serial = Serial('/dev/ttyUSB0', 2400)
sg = Stargate(serial)
sg.start()

# Listen for changes on Digital Input #1 on Stargate
sg.onCommand(callback=on_digital_input, address='D1')

# Code is done, we no longer need the interface
sg.shutdown()

