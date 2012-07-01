Pytomation
==========

Python Home Automation

Supports the following interfaces:
- Insteon / X10 (2412N, 2412S)
- UPB (Universal Powerline Bus) (Serial PIM)

Future:
- JDS Stargate (RS232 / RS485)

EXAMPLE OF USE: 
--------------- example_insteon_use.py ---------------------------
from pytomation.interfaces import InsteonPLM, TCP
#serial = Serial('/dev/ttyUSB0', 19200)
#insteon = InsteonPLM(serial)
# or
tcp = TCP('192.168.13.146', 9761)
insteon = InsteonPLM(tcp)
insteon.start()

# Turn on Light - Address 19.05.7b
response = insteon.on('19.05.7b')

# Turn off Light - Address 19.05.7b
response2 = insteon.off('19.05.7b')

# Check for success
if response:
    print "Message was successfully sent!"
else:
    print "Interface not responding"

# Code is done, we no longer need the interface
insteon.shutdown()
tcp.shutdown()
-----------------------------------------------------------------


---------------- example_upb_use.py -----------------------------
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

# Code is done, we no longer need the interface
upb.shutdown()
------------------------------------------------------------
