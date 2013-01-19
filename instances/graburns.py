import select

from pytomation.interfaces import UPB, InsteonPLM, TCP, Serial, Stargate, W800rf32, \
                                    NamedPipe, StateInterface, Command
from pytomation.devices import Motion2, Door2, Light2, Location2, Interface2Device, \
                                Photocell2, Generic2, State2Device, State2, Attribute

from pytomation.common.system import *

###################### INTERFACE CONFIG #########################
upb = UPB(Serial('/dev/ttyMI0', 4800))

#insteon = InsteonPLM(TCP('192.168.13.146', 9761))
insteon = InsteonPLM(Serial('/dev/ttyMI1', 19200, xonxoff=False))

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

# My camera motion software will echo a "motion" to this pipe.
pipe_front_yard_motion = StateInterface(NamedPipe('/tmp/front_yard_motion'))


###################### DEVICE CONFIG #########################

#doors
d_foyer = Door2('D1', sg, name='Foyer Door')
d_laundry = Door2('D2', sg, name='Laundry Door')
d_garage = Door2('D3', sg, name='Garage Door')
d_garage_overhead = Door2((49, 38, 'L'), upb, name='Garage Overhead')
d_porch = Door2('D5', sg, name='Porch Door')
d_basement = Door2('D6', sg, name='Basement')
d_master = Door2('D4', sg, name='Master')
d_crawlspace = Door2('D10', sg, name='Crawlspace Door')
d_pool = Door2('D11', sg, name='Pool Door')

#general input
i_laundry_security = Generic2('D7', sg, name='Laundry Keypad')
i_master_security = Generic2('D9', sg, name='Master Keypad')
i_laser_perimeter = Generic2('D12', sg, name='Laser Perimeter')

#motion
# Motion sensor is hardwired and immediate OFF.. Want to give it some time to still detect motion right after
m_family = Motion2(address='D8', 
                  devices=(sg),
                  delay={
                         Attribute.COMMAND: Command.STILL,
                         Attribute.SECS: 30,
                         },
                  name='Family Motion'
                  )

m_front_porch = Motion2(address='F1',
                devices=w800,
                name='Front Porch Motion',
                )
ph_front_porch = Photocell2(address='F2',
                devices=w800)
m_front_garage = Motion2(address='F3',
                devices=w800,
                name='Front Garage Motion')
ph_front_garage = Photocell2(address='F4',
                devices=w800)
m_front_driveway = Motion2(address='F5',
                devices=w800,
                name='Front Driveway Motion')
ph_front_driveway = Photocell2(address='F6',
                devices=w800)
m_front_camera = Motion2(address=None,
                      devices=pipe_front_yard_motion)

m_garage = Motion2(address='G1',
                  devices=w800,
                  name='Garage Motion')
ph_garage = Photocell2(address='G2',
                  devices=w800)

m_utility = Motion2(address='G3',
                  devices=w800,
                  name='Utility Motion')
ph_utility = Photocell2(address='G4',
                  devices=w800)

m_breakfast = Motion2(address='G7',
                  devices=w800,
                  name='Breakfast Motion')
ph_breakfast = Photocell2(address='G8',
                  devices=w800)

m_foyer = Motion2(address='G5',
                  devices=w800,
                  name='Foyer Motion')
ph_foyer = Photocell2(address='G6',
                  devices=w800)

m_den = Motion2(address='G9',
                  devices=w800,
                  name='Den Motion')
ph_den = Photocell2(address='GA',
                  devices=w800)

m_kitchen = Motion2(address='GB',
                  devices=w800,
                  name='Kitchen Motion')
ph_kitchen = Photocell2(address='GC',
                  devices=w800)

#keypads
k_master = Generic2(
                           address=(49,8),
                           devices=(upb,),
                           name='Master Bed Keypad'
                           )

#Scenes
#s_all_indoor_off = InterfaceDevice(
#                 address=(49,4,'L'),
#                 devices=(upb,),
#                 )

s_all_indoor_off = State2Device()

#photocell
ph_standard = Location2('35.2269', '-80.8433', 
                       tz='US/Eastern', 
                       mode=Location2.MODE.STANDARD, 
                       is_dst=True,
                       name='Standard Photocell')
ph_civil = Location2('35.2269', '-80.8433', 
                    tz='US/Eastern', 
                    mode=Location2.MODE.CIVIL, 
                    is_dst=True,
                    name='Civil Photocell')

#lights
# Turn on the foyer light at night when either the door is opened or family PIR is tripped.
l_foyer = Light2(
                address=(49, 3),
                devices=(upb, d_foyer,
                         m_foyer,
                         ph_standard),
                 ignore=({
                         Attribute.COMMAND: Command.DARK,
                         },
                         {
                          Attribute.COMMAND: Command.STILL}
            			 ),
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

l_front_porch = Light2(
                      address=(49, 4),
                      devices=(upb, d_foyer, m_front_porch, m_front_camera, ph_standard, ),
                      initial=ph_standard,
                      delay={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.SECS: 3*60,
                             },
                       idle={
                             Attribute.COMMAND:(Command.LEVEL, 40),
                             Attribute.SECS: 10*60,
                             },
                       time={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.TIME: '11:59pm',
                             },
                      name='Front Porch Light'
                      )


l_front_flood = Light2(
                      address=(49, 5), 
                      devices=(upb, d_garage, d_garage_overhead, 
                               d_foyer, m_front_garage, m_front_camera, ph_standard),
                      delay={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.SECS: 3*60,
                             },
                       idle={
                             Attribute.COMMAND:(Command.LEVEL, 40),
                             Attribute.SECS: 5*60,
                             },
                       time={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.TIME: '11:59pm',
                             },
                      name='Front Flood Light'
                      )

# Cron Format
#  secs=allMatch, min=allMatch, hour=allMatch, day=allMatch, month=allMatch, dow=allMatch
l_front_outlet = Light2(
                      address=(49, 21), 
                      devices=(upb, ph_civil),
                      initial=ph_civil,
#                      time_off='10:30pm',
# Im usually working on the code at this time of night, so lets send multiple off signals
# just in case I am not running pyto during its designated time.
#                      time_off=(0, 30, [22,23,0,01]),
                      name='Front Outlet Light'
                      )

l_front_garage = Light2(
                      address=(49, 2), 
                      devices=(upb, d_garage, d_garage_overhead, 
                               m_front_garage, m_front_camera, ph_standard),
                      delay={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.SECS: 3*60,
                             },
                       idle={
                             Attribute.COMMAND:(Command.LEVEL, 40),
                             Attribute.SECS: 10*60,
                             },
                       time={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.TIME: '11:59pm',
                             },
                      name='Front Garage Light',
                      )

l_garage = Light2(
                      address=(49, 18), 
                      devices=(upb, m_garage, d_garage, d_garage_overhead, 
                               ph_standard, s_all_indoor_off),
                      delay={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.SECS: 5*60,
                             },
                       time={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.TIME: '11:59pm',
                             },
                      name='Garage Light',
                      sync=True, #Un-reliable connection this far
                      )

l_family_lamp = Light2(
                address=(49, 6), 
                devices=(upb, m_family, ph_standard),
                mapped={
                        Attribute.COMMAND: (Command.MOTION, Command.LIGHT),
                        Attribute.TARGET: Command.OFF,
                        Attribute.SECS: 30*60
                        },
                ignore={
                        Attribute.COMMAND: (Command.STILL, Command.DARK),
                        },
                name='Family Lamp Light',
                )

l_family = Light2(
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


##################### USER CODE ###############################
#Manually controlling the light
#l_foyer.on()
#l_foyer.off()
#l_front_porch.on()
#l_front_porch.off()
#l_family_lamp.l40()

def MainLoop(*args, **kwargs):
#    print 'Im in a main loop!'
#    if l_foyer.state == State.ON:
#        l_foyer.off()
#    else:
#        l_foyer.on()
    pass
        

# Start the whole system.  pytomation.common.system.start()
start(
      loop_action=MainLoop,
      loop_time=1, # Loop every 1 sec
      admin_user='pyto',
      admin_password='mation'
      )



