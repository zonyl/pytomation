import select

from pytomation.interfaces import UPB, InsteonPLM, TCP, Serial, Stargate
from pytomation.devices import Motion, Door, Light, Location
###################### INTERFACE CONFIG #########################
upb = UPB(Serial('/dev/ttyMI0', 4800))
#upb.start()

#insteon = InsteonPLM(TCP('192.168.13.146', 9761))
#insteon.start()

sg = Stargate(Serial('/dev/ttyMI2', 9600))
#sg.start()

###################### DEVICE CONFIG #########################

d_foyer = Door('D1', sg)
l_foyer = Light((49, 3), (upb, d_foyer))
l_foyer.on()
l_foyer.off()


# sit and spin - Let the magic flow
select.select([],[],[])
