pytomation
==========

Python Home Automation

Support the following interfaces:
- Insteon / X10 (2412N, 2412S)
- UPB (Universal Powerline Bus) (Serial PIM)

Future:
- JDS Stargate (RS232)

EXAMPLE OF USE: 

---------------- example_use.py -----------------------------
from pytomation.interfaces import UPB, Serial

serial = Serial('/dev/ttyUSB0', 4800)
upb = UPB(serial)
upb.start()

# Turn on Light - Network: 49, ID: 3
response = upb.on((49, 3))

# Check for success
if response:
    print "Message was successfully sent!"
else:
    print "Interface not responding"

# Code is down, we no longer need the interface
upb.shutdown()
------------------------------------------------------------
