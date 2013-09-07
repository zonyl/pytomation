import select

from pytomation.interfaces import UPB, InsteonPLM, TCP, Serial, Stargate, W800rf32, \
                                    NamedPipe, StateInterface, Command, HTTPServer, \
                                    HTTP, HW_Thermostat, WeMo
from pytomation.devices import Motion, Door, Light, Location, InterfaceDevice, \
                                Photocell, Generic, StateDevice, State, Attribute, \
                                Room, Thermostat, XMPP_Client

#from pytomation.common.system import *

###################### INTERFACE CONFIG #########################
web = HTTPServer()

xmpp = XMPP_Client(id='pytomation@sharpee.com', password='password', server='talk.google.com', port=5222)

upb = UPB(Serial('/dev/ttyMI0', 4800))

#insteon = InsteonPLM(TCP('192.168.13.146', 9761))
insteon = InsteonPLM(Serial('/dev/ttyMI1', 19200, xonxoff=False))

w800 = W800rf32(Serial('/dev/ttyMI3', 4800)) 

sg = Stargate(Serial('/dev/ttyMI4', 9600))
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

# My camera motion software will echo a "motion" to this pipe.
pipe_front_yard_motion = StateInterface(NamedPipe('/tmp/front_yard_motion'))

thermostat_upstairs = Thermostat(devices=HW_Thermostat(HTTP(host='192.168.13.211'), poll=60), name='Thermostat Upstairs')
thermostat_downstairs = Thermostat(devices=HW_Thermostat(HTTP(host='192.168.13.210'), poll=60), name='Thermostat Downstairs')

###################### DEVICE CONFIG #########################

#doors
d_foyer = Door('D1', sg, name='Foyer Door')
d_laundry = Door('D2', sg, name='Laundry Door')
d_garage = Door('D3', sg, name='Garage Door')
#d_garage_overhead = Door((49, 38, 'L'), upb, name='Garage Overhead')
d_garage_overhead = Door("19.bc.06", insteon, name='Garage Overhead')
d_porch = Door('D5', sg, name='Porch Door')
d_basement = Door('D6', sg, name='Basement')
d_master = Door('D4', sg, name='Master')
d_crawlspace = Door('D10', sg, name='Crawlspace Door')
d_pool = Door('D11', sg, name='Pool Door')

xmpp.add_device(d_garage)
xmpp.add_device(d_garage_overhead)
xmpp.mapped(command=Command.OPEN,
            mapped=(Command.MESSAGE, 'jason@sharpee.com', 'Garage door was opened!'),
            )

#general input
i_laundry_security = Generic('D7', sg, name='Laundry Keypad')
i_master_security = Generic('D9', sg, name='Master Keypad')
i_laser_perimeter = Generic('D12', sg, name='Laser Perimeter')

#motion
# Motion sensor is hardwired and immediate OFF.. Want to give it some time to still detect motion right after
m_family = Motion(address='D8', 
                  devices=(sg),
                  delay={
                         Attribute.COMMAND: Command.STILL,
                         Attribute.SECS: 30,
                         },
                  name='Family Motion'
                  )

m_front_porch = Motion(address='F1',
                devices=w800,
                name='Front Porch Motion',
                )
ph_front_porch = Photocell(address='F2',
                devices=w800)
m_front_garage = Motion(address='F3',
                devices=w800,
                name='Front Garage Motion')
ph_front_garage = Photocell(address='F4',
                devices=w800)
m_front_driveway = Motion(address='F5',
                devices=w800,
                name='Front Driveway Motion')
ph_front_driveway = Photocell(address='F6',
                devices=w800)
m_front_camera = Motion(address=None,
                      devices=pipe_front_yard_motion)

m_garage = Motion(address='G1',
                  devices=w800,
                  name='Garage Motion')
ph_garage = Photocell(address='G2',
                  devices=w800)

m_utility = Motion(address='G3',
                  devices=w800,
                  name='Utility Motion')
ph_utility = Photocell(address='G4',
                  devices=w800)

m_breakfast = Motion(address='G7',
                  devices=w800,
                  name='Breakfast Motion')
ph_breakfast = Photocell(address='G8',
                  devices=w800)

m_foyer = Motion(address='G5',
                  devices=w800,
                  name='Foyer Motion')
ph_foyer = Photocell(address='G6',
                  devices=w800)

m_den = Motion(address='G9',
                  devices=w800,
                  name='Den Motion')
ph_den = Photocell(address='GA',
                  devices=w800)

m_kitchen = Motion(address='GB',
                  devices=w800,
                  name='Kitchen Motion')
ph_kitchen = Photocell(address='GC',
                  devices=w800)

#keypads
k_master = Generic(
                           address=(49,8),
                           devices=(upb,),
                           name='Master Bed Keypad'
                           )

#Scenes
#s_all_indoor_off = InterfaceDevice(
#                 address=(49,4,'L'),
#                 devices=(upb,),
#                 )

s_all_indoor_off = StateDevice()

#photocell
ph_standard = Location('35.2269', '-80.8433', 
                       tz='US/Eastern', 
                       mode=Location.MODE.STANDARD, 
                       is_dst=True,
                       name='Standard Photocell')
ph_civil = Location('35.2269', '-80.8433', 
                    tz='US/Eastern', 
                    mode=Location.MODE.CIVIL, 
                    is_dst=True,
                    name='Civil Photocell')

# Rooms
r_foyer = Room(name='Foyer', devices=(m_foyer))
r_den = Room(name='Den', devices=(m_den, r_foyer))
r_family = Room(name='Family', 
		devices=(m_family, r_foyer),
		trigger={ Attribute.COMMAND: Command.OCCUPY,
			  Attribute.MAPPED: Command.VACATE,
			  Attribute.SECS: 2*60*60,
			},
		)
r_kitchen = Room(name='Kitchen', devices=(m_kitchen, r_foyer))
r_foyer.add_device(r_den)
r_foyer.add_device(r_family)
r_foyer.add_device(r_kitchen)
r_breakfast = Room(name='Breakfast', devices=(m_breakfast, r_kitchen))
r_utility = Room(name='Utility', devices=(m_utility, r_kitchen, d_laundry))
r_kitchen.add_device(r_breakfast)
r_kitchen.add_device(r_utility)
r_garage = Room(name='Garage', devices=(m_garage, r_utility, d_laundry, d_garage, d_garage_overhead))
r_utility.add_device(r_garage)

#lights
# Turn on the foyer light at night when either the door is opened or family PIR is tripped.
l_foyer = Light(
                address="24.a9.14",
                devices=(insteon, d_foyer,
                         m_foyer,
                         ph_standard),
                 ignore={
                         Attribute.COMMAND: (Command.DARK, Command.STILL,)
                         },
                 time={
                       Attribute.TIME: '11:59pm',
                       Attribute.COMMAND: Command.OFF
                       },
                 mapped={
                         Attribute.COMMAND: (
                                             Command.MOTION, Command.OPEN,
                                              Command.CLOSE, Command.LIGHT,
                                              ),
                         Attribute.MAPPED: Command.OFF,
                         Attribute.SECS: 2*60,
                         },
		 name='Foyer Light',
                )

l_front_porch = Light(
                      address="24.9d.55",
                      devices=(insteon, d_foyer, m_front_porch, m_front_camera, ph_standard),
                      initial=ph_standard,
                      delay=({
                             Attribute.COMMAND: Command.OFF,
                             Attribute.SECS: 10*60*60,
                             },
                             {
                              Attribute.COMMAND: Command.OFF,
                              Attribute.SECS: 0,
                              Attribute.SOURCE: (ph_standard, web,)
                              },
                             ),
                       idle={
                             Attribute.MAPPED:(Command.LEVEL, 30),
                             Attribute.SECS: 10*60,
                             },
                       time={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.TIME: '11:59pm',
                             },
                      name='Front Porch Light'
                      )


l_front_flood = Light(
                      address="24.6f.17", 
                      devices=(insteon, d_garage, d_garage_overhead, 
                               d_foyer, m_front_garage, m_front_camera, ph_standard),
                      delay=({
                             Attribute.COMMAND: Command.OFF,
                             Attribute.SECS: 10*60,
                             },
                             {
                              Attribute.COMMAND: Command.OFF,
                              Attribute.SECS: 0,
                              Attribute.SOURCE: (ph_standard, web,)
                              },
                             ),
                       idle={
                             Attribute.MAPPED:(Command.LEVEL, 30),
                             Attribute.SECS: 5*60,
                             },
                       time={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.TIME: '11:59pm',
                             },
                      trigger={
                               Attribute.COMMAND: Command.ON,
                               Attribute.MAPPED: Command.OFF,
                               Attribute.SECS: 10*60,
                               },
                      name='Front Flood Light'
                      )

# Cron Format
#  secs=allMatch, min=allMatch, hour=allMatch, day=allMatch, month=allMatch, dow=allMatch
l_front_outlet = Light(
                      address=(49, 21), 
                      devices=(upb, ph_civil),
                      initial=ph_civil,
#                      time_off='10:30pm',
# Im usually working on the code at this time of night, so lets send multiple off signals
# just in case I am not running pyto during its designated time.
#                      time_off=(0, 30, [22,23,0,01]),
                      name='Front Outlet Light'
                      )

l_front_garage = Light(
                      address="24.9d.7c", 
                      devices=(insteon, d_garage, d_garage_overhead, 
                               m_front_garage, m_front_camera, ph_standard),
                      delay=({
                             Attribute.COMMAND: Command.OFF,
                             Attribute.SECS: 10*60*60,
                             },
                             {
                              Attribute.COMMAND: Command.OFF,
                              Attribute.SECS: 0,
                              Attribute.SOURCE: (ph_standard, web,)
                              },
                             ),
                       idle={
                             Attribute.MAPPED:(Command.LEVEL, 30),
                             Attribute.SECS: 10*60,
                             },
                       time={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.TIME: '11:59pm',
                             },
                      name='Front Garage Light',
                      )

l_garage = Light(
	              address='20.8b.40',    
                      devices=(insteon, m_garage, d_garage, d_garage_overhead, d_laundry, 
                               ph_standard, s_all_indoor_off),
                      delay=(
                             {
                                 Attribute.COMMAND: Command.OFF,
                                 Attribute.SECS: 5*60,
                             },
                             {
                                    Attribute.COMMAND: Command.OFF,
                                    Attribute.SECS: 0,
                                    Attribute.SOURCE: web,
                             },
                             ),
                       time={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.TIME: '11:59pm',
                             },
                      name='Garage Light',
                      sync=True, #Un-reliable connection this far
                      )

l_family_lamp = Light(
                address=(49, 6), 
#                devices=(upb, ph_standard, r_family),
                devices=(upb, ph_standard),
                mapped={
                        Attribute.COMMAND: (Command.MOTION, Command.LIGHT),
                        Attribute.TARGET: Command.OFF,
                        Attribute.SECS: 30*60
                        },
                ignore=({
                        Attribute.COMMAND: (Command.STILL, Command.DARK),
                        },
                        {
                         Attribute.COMMAND: (Command.MOTION, Command.OCCUPY),
                         Attribute.START: '12:00am',
                         Attribute.END: '6:00am',
                         }
                        ),
                delay={
                       Attribute.COMMAND: Command.OFF,
                       Attribute.SECS: 15*60,
                       Attribute.SOURCE: r_family,
                       },
		time={
			Attribute.COMMAND: Command.OFF,
			Attribute.TIME: '11:59pm',
			},

                name='Family Lamp Light',
                )

l_family = Light(
                 address='19.05.7b',    
                 devices=(insteon, m_family, ph_standard),
                 name='Family Light',
                mapped={
                        Attribute.COMMAND: (Command.MOTION, Command.LIGHT),
                        Attribute.TARGET: Command.OFF,
                        Attribute.SECS: 30*60
                        },
                ignore={
                        Attribute.COMMAND: (Command.STILL, Command.DARK),
                        },
                 )

l_bed_hallway = Light(
                 address='19.0d.1b',    
                 devices=(insteon,),
                 name='Bed Hallway Light',
                 )

l_playroom = Light(devices = WeMo('192.168.13.141', '49153'), 
                  name = 'Playroom')

##################### USER CODE ###############################
#Manually controlling the light
#l_foyer.on()
#l_foyer.off()
#l_front_porch.on()
#l_front_porch.off()
#l_family_lamp.l40()

upb.update_status()

def MainLoop(startup=False, *args, **kwargs):
    if startup:
        print 'Run once'
        
#    print 'Im in a main loop!'
#    if l_foyer.state == State.ON:
#        l_foyer.off()
#    else:
#        l_foyer.on()
    pass
        





