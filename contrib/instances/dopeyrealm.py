# import the standard python modules "select" and "time"
import select
import time

# Import all the Pytomation interfaces we are going to use.
from pytomation.interfaces import InsteonPLM, Serial, HTTP, VenstarThermostat, Command, PytoWebSocketServer, Open_zwave

# Import all the Pytomation Devices we will use.
from pytomation.devices import Attribute, Light, Location, Thermostat, Room, Door, Lock
#from pytomation.devices.scene import Scene

#Web Server
websocket = PytoWebSocketServer()

#Interfaces
insteon = InsteonPLM(Serial('/dev/insteon', 19200, xonxoff=False))
ozw = Open_zwave(serialDevicePath="/dev/zwave",config_path="/etc/openzwave")

#Thermostat (override available commads)
thermostat_commands = [Command.AUTOMATIC, Command.COOL, Command.HEAT, Command.HOLD, Command.SCHEDULE, Command.OFF, Command.LEVEL, Command.CIRCULATE, Command.STILL, Command.VACATE, Command.OCCUPY, Command.SETPOINT]
hall_thermostat = Thermostat(commands = thermostat_commands, name="Thermostat", devices=VenstarThermostat(HTTP(host='HallThermostat')))

#Sensors
ph_calculated = Location('38.576492', '-121.493375',
                         tz='America/Los_Angeles',
                         mode=Location.MODE.STANDARD,
                         is_dst=True,
                         name='Calculated Photocell')

#Front Door sensor, remove non functional status command
d_front_door = Door(address='2A.F9.B7',
                     devices=(insteon),
                     name="Front Door Sensor",
                     commands=[Command.OPEN, Command.CLOSE])

#Front Door Deadbolt (key set in config.xml, in config_path)
lk_front_door = Lock(address='4',devices=(ozw,d_front_door),name="Front Door Deadbolt",
                      mapped={Attribute.COMMAND: Command.CLOSE,
                              Attribute.MAPPED: Command.LOCK})

#Lights
l_office = Light(address='5',devices=ozw,name='Office Light')

l_livingroom = Light(address="7",devices=ozw,name="Living Room Light")

l_backporch = Light(address='2A.74.38',
                    devices=(insteon, ph_calculated),
                    name="Back Porch Light")

l_frontporch = Light(address='2A.56.58',
                     devices=(insteon, ph_calculated),
                     name="Front Porch Light")

l_kitchen_recessed = Light(address='2A.31.66',
                           devices=(insteon),
                           name="Kitchen Recessed Light")

l_kitchen_back = Light(address='2A.74.6D',
		devices=(insteon),
		name="Kitchen Light")

l_kitchen_faucet = Light(address='2A.81.FD',
		devices=(insteon),
		name="Kitchen Faucet Light")

l_bathroom = Light(address='2A.3F.9F',
		devices=(insteon),
		verify_on_level = True,
		name="Bathroom Light")

f_bathroom = Light(address='21.8D.F5',
		devices=(insteon),
		name="Bathroom Fan")

l_foyer = Light(address='2A.57.E7',
		devices=(insteon),
		name="Foyer Light")

l_hallway = Light(address='2A.B8.F8',
        devices=(insteon),
        name="Hallway Light")

l_hallway_switch = Light(address='2A.EB.30',
        devices=(insteon),
        name="Hallway Light Switch")

l_master_bathroom = Light(address='2A.B2.AF',
                devices=(insteon),
                name="Master Bathroom Light")

l_master_faucet = Light(address='2A.9C.D9',
                devices=(insteon),
                name="Master Faucet Light")

# KeypadLinc Buttons as Scenes (under construction, not currently functional)
# s_kitchen_back_linc = Scene(address='2A.31.66.02',
#                         devices=(insteon),
#                         responders={l_kitchen_back: {'state': 'ON'},},
#                         name = 'Kitchen Back Light')
# 
# s_kitchen_faucet_linc = Scene(address='2A.31.66.03',
#                         devices=(insteon),
#                         responders={l_kitchen_faucet: {'state': 'ON'},},
#                         name = 'Kitchen Faucet Light Linc')
# 
# s_backporch_linc = Scene(address='2A.31.66.04',
#                         devices=(insteon),
#                         responders={l_backporch: {'state': 'ON'},},
#                         name = 'Back Porch Light Linc')
# 
# s_frontporch_linc = Scene(address='2A.31.66.05',
#                         devices=(insteon),
#                         responders={l_frontporch: {'state': 'ON'},},
#                         name = 'Front Porch Light Linc')
# 
# s_foyer_linc = Scene(address='2A.31.66.06',
#                         devices=(insteon),
#                         responders={l_foyer: {'state': 'ON'},},
#                         name = 'Foyer Light Linc')
# 
# s_hallway_linc = Scene(address='2A.31.66.07',
#                         devices=(insteon),
#                         responders={l_hallway: {'state': 'ON'},l_hallway_switch: {'state': 'ON'}},
#                         name = 'Hallway Light Linc')

#Rooms (Device Grouping shouldn't add default command mappings, but does. Ignoring devices works-around. Fix under construction) 
r_backporch = Room(name='Back Porch', devices=l_backporch)
r_frontporch = Room(name='Front Porch', devices=l_frontporch)
r_kitchen = Room(name='Kitchen', ignore={Attribute.COMMAND: Command.LEVEL, Attribute.SOURCE: hall_thermostat}, source=l_kitchen_back, devices=(l_kitchen_recessed, l_kitchen_back, l_kitchen_faucet, hall_thermostat))
r_bathroom = Room(name='Bathroom', ignore={Attribute.COMMAND: Command.LEVEL, Attribute.SOURCE: hall_thermostat}, source=l_bathroom, devices=(l_bathroom, f_bathroom, hall_thermostat))
r_foyer = Room(name='Foyer', ignore={Attribute.COMMAND: Command.LEVEL, Attribute.SOURCE: hall_thermostat}, devices=(l_foyer, hall_thermostat))
r_hallway = Room(name='Hallway', ignore={Attribute.COMMAND: Command.LEVEL, Attribute.SOURCE: hall_thermostat}, devices=(l_hallway, hall_thermostat))
r_livingroom = Room(name='Master Bedroom', ignore={Attribute.COMMAND: Command.LEVEL, Attribute.SOURCE: hall_thermostat}, devices=(l_livingroom, hall_thermostat))
r_office = Room(name='Office', ignore={Attribute.COMMAND: Command.LEVEL, Attribute.SOURCE: hall_thermostat}, devices=(l_office, hall_thermostat))
r_master_bathroom = Room(name='Master Bathroom', ignore={Attribute.COMMAND: Command.LEVEL, Attribute.SOURCE: hall_thermostat}, devices=(l_master_bathroom, hall_thermostat))
r_master_bedroom = Room(name='Master Bedroom', ignore={Attribute.COMMAND: Command.LEVEL, Attribute.SOURCE: hall_thermostat}, devices=(l_master_faucet, hall_thermostat))

#Nested Rooms (Under construction, not currently functional)
#r_house = Room(name='House', devices=(r_kitchen, r_bathroom, r_foyer, r_hallway, r_master_bathroom, r_master_bedroom))
#r_outside = Room(name='Outside', devices=(r_backporch, r_frontporch))


def MainLoop(startup=False, *args, **kwargs):
    def kitchen_back_onStateChanged(state, source, prev, device):
        if type(source) is InsteonPLM:
            l_kitchen_faucet.set_state(state)
    
    def hallway_onStateChanged(state, source, prev, device):
        if l_hallway_switch._state != state:
            try:
                if type(source) is InsteonPLM:
                    l_hallway_switch.set_state(state)
                elif type(state) is tuple:
                    l_hallway_switch.level(state[1])
                elif state == 'on':
                    l_hallway_switch.on()
                elif state != 'unknown':
                    l_hallway_switch.off()
            except:
                pass
    
    def hallway_switch_onStateChanged(state, source, prev, device):
        if l_hallway._state != state:
            try:
                if type(source) is InsteonPLM:
                    l_hallway.set_state(state)
                elif type(state) is tuple:
                    l_hallway.level(state[1])
                elif state == 'on':
                    l_hallway.on()
                elif state != 'unknown':
                    l_hallway.off()
            except:
                pass
        
    if startup:
        time.sleep(5)
        #Insteon Controlled linked devices, three-way switch, ensure state gets changed
        l_hallway.onStateChanged(hallway_onStateChanged)
        l_hallway_switch.onStateChanged(hallway_switch_onStateChanged)
        
        #Get status individually, to prevent door sensor request from blocking (doesn't accept status)
        l_backporch.status(timeout=10)
        l_frontporch.status(timeout=10)
        l_kitchen_recessed.status(timeout=10)
        l_kitchen_back.status(timeout=10)
        l_kitchen_faucet.status(timeout=10)
        l_bathroom.status(timeout=10)
        f_bathroom.status(timeout=10)
        l_foyer.status(timeout=10)
        l_hallway.status(timeout=10)
        l_master_bathroom.status(timeout=10)
        l_master_faucet.status(timeout=10)
        
        #Insteon Controlled linked devices, ensure state gets changed
        l_kitchen_back.onStateChanged(kitchen_back_onStateChanged)
