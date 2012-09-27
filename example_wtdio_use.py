import select
#import time
from pytomation.interfaces import WTDIO, Serial 


def on_digital_input(command=None, address=None):
    print "Weeder Digital Input Board " + address[0] + " Channel " + address[1] + " -> " + command

serial = Serial('/dev/mh_weeder_port', 9600)
wtdio = WTDIO(serial)
wtdio.start()

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
# I'll change this later to make full use of the weeder boards 
# capabilities
wtdio.setChannel('ASA')
wtdio.setChannel('ASB')
wtdio.setChannel('ASC')
wtdio.setChannel('ASD')
wtdio.setChannel('ASE')
wtdio.setChannel('ASF')
wtdio.setChannel('ASG')
wtdio.setChannel('ASH')
wtdio.setChannel('ALI')
wtdio.setChannel('ALJ')
wtdio.setChannel('ALK')
wtdio.setChannel('ALL')
wtdio.setChannel('ALM')
wtdio.setChannel('ALN')

# Listen for changes on Digital Inputs on wtdio
wtdio.onCommand(callback=on_digital_input)
# Set outputs 
#resp = wtdio.on(board='A', channel='I')

# Code is done, we no longer need the interface
#wtdio.shutdown()
	
# sit and spin - Let the magic flow
select.select([],[],[])
