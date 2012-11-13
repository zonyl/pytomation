from pytomation.config import *
from pytomation.interfaces import UPB, Serial

debug['UPB'] = 1
serial = Serial('/dev/ttyUSB0', 4800)
upb = UPB(serial)
upb.start()

# Turn on Light - Network: 49, ID: 3
response = upb.on((49, 3))

# Turn off Light - Network: 49, ID: 3
response2 = upb.off((49, 3))

# Check for success
if response:
    print "Message was successfully sent!"
else:
    print "Interface not responding"

# Code is done, we no longer need the interface
upb.shutdown()
