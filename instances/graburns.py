import select

from pytomation.interfaces import UPB, InsteonPLM, TCP, Serial, Stargate
from pytomation.devices import Motion, Door, Light, Location
###################### INTERFACE CONFIG #########################
upb = UPB(Serial('/dev/ttyMI0', 4800))

#insteon = InsteonPLM(TCP('192.168.13.146', 9761))
#insteon.start()

sg = Stargate(Serial('/dev/ttyMI2', 9600))
# invert the DIO channels for these contact sensors
sg.dio_invert(1)
sg.dio_invert(8)

###################### DEVICE CONFIG #########################

d_foyer = Door('D1', sg)

m_family = Motion('D8', sg)
# Motion sensor is hardwired and immediate OFF.. Want to give it some time to still detect motion right after
m_family.delay_still(2*60) 

ph_sun = Location('35.2269', '-80.8433', tz='US/Eastern', mode=Location.MODE.STANDARD, is_dst=True)

# Turn on the foyer light at night when either the door is opened or family PIR is tripped.
l_foyer = Light((49, 3), (upb, d_foyer, m_family, ph_sun))
# After being turned on, turn off again after 2 minutes of inactivity.
l_foyer.delay_off(2*60)
# Turn off the light no matter what at 11:59pm
l_foyer.time_off('11:59pm')
# Do not turn on the light automatically when it is night time (indoor light)
# Only looks at dark for restricing the whether the light should come on
l_foyer.ignore_dark(True)

##################### USER CODE ###############################
#Manually controlling the light
l_foyer.on()
l_foyer.off()


# sit and spin - Let the magic flow
select.select([],[],[])
