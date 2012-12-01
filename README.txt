Pytomation
==========

Python Home Automation

Supports the following interfaces:
- Insteon / X10 (2412N, 2412S)
- UPB (Universal Powerline Bus) (Serial PIM)
- JDS Stargate (RS232 / RS485)
- Weeder Digital I/O board (Wtdio/RS232)
- W800RF32 X10 RF receiver (W800/RS232)

Future:
- Z-Wave (Aeon Labs) DSA02203-ZWUS


EXAMPLE OF USE: 
--------------- example_insteon_use.py ---------------------------
from pytomation.interfaces import InsteonPLM, TCP
#serial = Serial('/dev/ttyUSB0', 19200)
#insteon = InsteonPLM(serial)
# or
tcp = TCP('192.168.13.146', 9761)
insteon = InsteonPLM(tcp)

# Turn on Light - Address 19.05.7b
response = insteon.on('19.05.7b')

# Turn off Light - Address 19.05.7b
response2 = insteon.off('19.05.7b')

# Check for success
if response:
    print "Message was successfully sent!"
else:
    print "Interface not responding"

-----------------------------------------------------------------


---------------- example_upb_use.py -----------------------------
from pytomation.interfaces import UPB, Serial

serial = Serial('/dev/ttyUSB0', 4800)
upb = UPB(serial)

# Turn on Light - Network: 49, ID: 3
response = upb.on((49, 3))

# Check for success
if response:
    print "Message was successfully sent!"
else:
    print "Interface not responding"

------------------------------------------------------------

---------------- example_stargate_use.py -----------------------------
from pytomation.interfaces import Stargate, Serial


def on_digital_input(command=None, address=None):
    print "Digital Input #" + str(address) + " -> " + command


serial = Serial('/dev/ttyUSB0', 2400)
sg = Stargate(serial)

# Listen for changes on Digital Input #1 on Stargate
sg.onCommand(callback=on_digital_input, address='D1')

------------------------------------------------------------

---------------- example_wtdio_use.py -----------------------------
from pytomation.interfaces import WTDIO, Serial 

def on_digital_input(command=None, address=None):
    print "Weeder Digital Input Board " + address[0] + " Channel " + address[1] + " -> " + command

serial = Serial('/dev/ttyS0', 9600)
wtdio = WTDIO(serial)

# Set the I/O channels on the WTDIO board according to the command set
# S = Switch, L = Output default low
#
# Inputs are set according to the wtdio manual by sending the board 
# data in the following sequence.  BOARD TYPE CHANNEL
# Example:  Board 'A', Type SWITCH, Channel D  - 'ASD'
# Currently only SWITCH inputs are handled.
#
# Outputs are set as follows: BOARD LEVEL CHANNEL
# Example:  Board 'A', Level LOW, Channel 'M', - 'ALM'
#
wtdio.setChannel('ASA') #Channel A is input
wtdio.setChannel('ASB') #   "    B  "   "
wtdio.setChannel('ALM') #   "    M  " output
wtdio.setChannel('ALN') #   "    N  "   "

# Listen for changes on Digital Inputs on wtdio
wtdio.onCommand(callback=on_digital_input)
# Set outputs 
resp = wtdio.on(board='A', channel='M')

------------------------------------------------------------
