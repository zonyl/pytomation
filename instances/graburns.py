import select

from pytomation.interfaces import UPB, InsteonPLM, TCP, Serial, Stargate, W800rf32
from pytomation.devices import Motion, Door, Light, Location, InterfaceDevice, Photocell
###################### INTERFACE CONFIG #########################
upb = UPB(Serial('/dev/ttyMI0', 4800))

#insteon = InsteonPLM(TCP('192.168.13.146', 9761))
insteon = InsteonPLM(Serial('/dev/ttyMI1', 19200))

w800 = W800rf32(Serial('/dev/ttyMI3', 4800)) 

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
i_laundry_security = InterfaceDevice('D7', sg)
i_master_security = InterfaceDevice('D9', sg)
i_laser_perimeter = InterfaceDevice('D12', sg)

#motion
# Motion sensor is hardwired and immediate OFF.. Want to give it some time to still detect motion right after
m_family = Motion(address='D8', 
                  devices=(sg),
                  delay_still=2*60
                  )

m_front_porch = Motion(address='F1',
                devices=w800)
ph_front_porch = Photocell(address='F2',
                devices=w800)
m_front_garage = Motion(address='F3',
                devices=w800)
ph_front_garage = Photocell(address='F4',
                devices=w800)


#keypads
k_master = InterfaceDevice(
                           address=(49,8),
                           devices=(upb,),
                           )

#Scenes
s_all_indoor_off = InterfaceDevice(
                 address=(49,4,'L'),
                 devices=(upb,),
                 )

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
                devices=(upb, d_foyer, ph_standard, s_all_indoor_off),
                delay_off=2*60,
                time_off='11:59pm',
                ignore_dark=True,
                )

l_front_porch = Light(
                      address=(49, 4), 
                      devices=(upb, d_foyer, m_front_porch, ph_standard, ),
                      initial_state=ph_standard,
                      delay_off=10*60,
                      time_off='11:59pm',
                      )


l_front_flood = Light(
                      address=(49, 5), 
                      devices=(upb, d_garage, d_garage_overhead, 
                               d_foyer, m_front_garage, ph_standard),
                      initial_state=ph_standard,
                      delay_off=5*60,
                      time_off='11:59pm',
                      )

l_front_outlet = Light(
                      address=(49, 21), 
                      devices=(upb, ph_standard),
                      initial_state=ph_standard,
                      time_off='10:30pm',
                      )

l_front_garage = Light(
                      address=(49, 2), 
                      devices=(upb, d_garage, d_garage_overhead, 
                               m_front_garage, ph_standard),
                      initial_state=ph_standard,
                      delay_off=10*60,
                      time_off='11:59pm',
                      )

l_garage = Light(
                      address=(49, 18), 
                      devices=(upb, d_garage, d_garage_overhead, 
                               ph_standard, s_all_indoor_off),
                      delay_off=10*60,
                      time_off='11:59pm',
                      ignore_dark=True,
                      )

l_family_lamp = Light(
                      address=(49, 6), 
                      devices=(upb, m_family, ph_standard, s_all_indoor_off),
                      delay_off=30*60,
                      time_off='11:59pm',
                      ignore_dark=True,
                      )

l_family = Light(
                 address='19.05.7b',    
                 devices=(insteon, s_all_indoor_off),
                 )


##################### USER CODE ###############################
#Manually controlling the light
#l_foyer.on()
#l_foyer.off()
#l_front_porch.on()
#l_front_porch.off()

##################### TELNET MANHOLE ##########################
from twisted.internet import reactor
from twisted.manhole import telnet
def createShellServer( ):
	print 'Creating shell server instance'
	factory = telnet.ShellFactory()
	port = reactor.listenTCP( 2000, factory)
	factory.namespace.update(
			{'l_family_lamp': l_family_lamp}
			)
	factory.username = 'pyto'
	factory.password = 'mation'
	print 'Listening on port 2000'
	return port

if __name__ == "__main__":
	reactor.callWhenRunning( createShellServer )
	reactor.run()

# sit and spin - Let the magic flow
select.select([],[],[])
