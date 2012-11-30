import select

from pytomation.interfaces import UPB, InsteonPLM, TCP, Serial, Stargate
from pytomation.devices import Motion, Door, Light, Location, InterfaceDevice
###################### INTERFACE CONFIG #########################
upb = UPB(Serial('/dev/ttyMI0', 4800))

insteon = InsteonPLM(TCP('192.168.13.146', 9761))
#insteon.start()

sg = Stargate(Serial('/dev/ttyMI2', 9600))
# invert the DIO channels for these contact sensors
sg.dio_invert(1)
sg.dio_invert(2)
sg.dio_invert(3)
sg.dio_invert(4)
sg.dio_invert(5)
sg.dio_invert(6)
sg.dio_invert(7)
sg.dio_invert(8)
sg.dio_invert(9)
sg.dio_invert(10)
sg.dio_invert(11)
sg.dio_invert(12)


###################### DEVICE CONFIG #########################

#doors
d_foyer = Door('D1', sg)
d_laundry = Door('D2', sg)
d_garage = Door('D3', sg)
d_garage_overhead = Door((49, 38, 'L'), upb)
d_porch = Door('D4', sg)
d_basement = Door('D5', sg)
d_master = Door('D6', sg)
d_crawlspace = Door('D10', sg)
d_pool = Door('D11', sg)

#general input
s_laundry_pad = InterfaceDevice('D7', sg)
s_master_pad = InterfaceDevice('D9', sg)
s_laser_perimeter = InterfaceDevice('D12', sg)

#motion
# Motion sensor is hardwired and immediate OFF.. Want to give it some time to still detect motion right after
m_family = Motion(address='D8', 
                  devices=(sg),
                  delay_still=2*60)

#photocell
ph_standard = Location('35.2269', '-80.8433', 
                       tz='US/Eastern', 
                       mode=Location.MODE.STANDARD, 
                       is_dst=True)
ph_civil = Location('35.2269', '-80.8433', 
                    tz='US/Eastern', 
                    mode=Location.MODE.CIVIL, 
                    is_dst=True)

#lights
# Turn on the foyer light at night when either the door is opened or family PIR is tripped.
l_foyer = Light(
                address=(49, 3), 
                devices=(upb, d_foyer, ph_standard),
                delay_off=2*60,
                time_off='11:59pm',
                ignore_dark=True,
                )

l_front_porch = Light(
                      address=(49, 4), 
                      devices=(upb, d_foyer, ph_standard),
                      delay_off=10*60,
                      time_off='11:59pm',
                      )


l_front_flood = Light(
                      address=(49, 5), 
                      devices=(upb, d_garage, d_garage_overhead, d_foyer, ph_standard),
                      delay_off=5*60,
                      time_off='11:59pm',
                      )

l_front_outlet = Light(
                      address=(49, 21), 
                      devices=(upb),
                      )

l_front_garage = Light(
                      address=(49, 2), 
                      devices=(upb, d_garage, d_garage_overhead, ph_standard),
                      delay_off=10*60,
                      time_off='11:59pm',
                      )

l_garage = Light(
                      address=(49, 18), 
                      devices=(upb, d_garage, d_garage_overhead, ph_standard),
                      delay_off=10*60,
                      time_off='11:59pm',
                      ignore_dark=True,
                      )

l_family_lamp = Light(
                      address=(49, 6), 
                      devices=(upb, m_family, ph_standard),
                      delay_off=30*60,
                      ignore_dark=True,
                      )

l_family = Light(
                 address='19.05.7b',
                 devices=(insteon),
                 )

##################### USER CODE ###############################
#Manually controlling the light
#l_foyer.on()
#l_foyer.off()
l_family.on()
l_family.off()

# sit and spin - Let the magic flow
select.select([],[],[])
