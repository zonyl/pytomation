import select
#import time
from pytomation.config import *
from pytomation.interfaces import W800RF32, Serial 


def on_digital_input(command=None, address=None):
    print "W800RF32 X10 Input Housecode " + address[0] + " Unit " + address[1] + " -> " + command

debug['W800'] = 0
debug['HAInterface'] = 0
serial = Serial('/dev/mh_w800_port', 4800)
w800 = W800RF32(serial)
w800.start()


# Listen for changes on Digital Inputs on wtdio
w800.onCommand(callback=on_digital_input, address='E1')
# Code is done, we no longer need the interface
#w800.shutdown()
	
# sit and spin - Let the magic flow
select.select([],[],[])
