# import the standard python module "select"
import select
import RPi.GPIO as GPIO

# Import all the Pytomation interfaces we are going to use.
from pytomation.interfaces import UPB, InsteonPLM, TCP, Serial, Stargate, W800rf32, NamedPipe, StateInterface, Command, RPIInput, InsteonPLM2, HTTPServer

# Import all the Pytomation Devices we will use.
from pytomation.devices import Motion, Door, Light, Location, InterfaceDevice, Photocell, Generic, StateDevice, State, Attribute, Scene, Controller

#Create PLM and setup Raspberry PI board and web server
#Note: Raspberry PI inputs require root access
insteon = InsteonPLM2(Serial('/dev/ttyUSB0', 19200, xonxoff=False))
GPIO.setmode(GPIO.BOARD)
web = HTTPServer(address='raspberrypi.home')

ph_standard = Location('53.55', '-113.5',
                       tz='Canada/Mountain',
                       mode=Location.MODE.STANDARD,
                       is_dst=True,
                       name='Standard Photocell')

ll_livingroom1 = Light (address='18.97.08', devices=(insteon), name="Living Room Lamp 1")
ll_livingroom2 = Light (address='14.27.D3', devices=(insteon), name="Living Room Lamp 2")

sl_livingroom1 = Light (address='17.F7.8C', devices=(insteon), name="Living Room Lamps")
sl_livingroom2 = Light (address='16.67.06', devices=(insteon), name="Living Room Lights")

kl_master1 = Light (address='15.64.1D', devices=(insteon), name="Master Bedroom")
sl_master2 = Light (address='16.18.DD', devices=(insteon), name="Master Bathroom")

#KeypadLinc button scenes
kl_mastera = Scene (address="00.00.F3", devices=(insteon,), name="Keypad A", controllers=[Controller(kl_master1, 3)])
kl_masterb = Scene (address="00.00.F4", devices=(insteon,), name="Keypad B", controllers=[Controller(kl_master1, 4)])
kl_masterc = Scene (address="00.00.F5", devices=(insteon,), name="Keypad C", controllers=[Controller(kl_master1, 5)])
kl_masterd = Scene (address="00.00.F6", devices=(insteon,), name="Keypad D", controllers=[Controller(kl_master1, 6)])

sl_outside1 = Light (
	address='14.E7.AD', 
	devices=(insteon,ph_standard), 
	initial=ph_standard, 
	time={Attribute.COMMAND: Command.OFF, Attribute.TIME: '1:00am'},
	name="Outside Back Light")

sl_outside2 = Light (
	address='14.E6.A8', 
	devices=(insteon,ph_standard), 
	initial=ph_standard, 
	time={Attribute.COMMAND: Command.OFF, Attribute.TIME: '1:00am'},
	name="Outside Garage Lights")

ol_outside1 = Light (address='13.FE.5D', devices=(insteon), name="Outside Outlet")

#Raspberry PI inputs
pi_laundry = StateInterface(RPIInput(3))	#BCM 2
cs_laundry = Door (address=None, devices=(pi_laundry), name="Laundry Window")

pi_basementbed = StateInterface(RPIInput(5))	#BCM 3
cs_basementbed = Door (address=None, devices=(pi_basementbed), name="Basement Bedroom Window")

pi_masterbed = StateInterface(RPIInput(7))	#BCM 4
cs_masterbed = Door (address=None, devices=(pi_masterbed), name="Master Bedroom")

pi_boysbed = StateInterface(RPIInput(8))	#BCM 14
cs_boysbed = Door (address=None, devices=(pi_boysbed), name="Boys Bedroom Window")

pi_kitchen = StateInterface(RPIInput(10))	#BCM 15
cs_kitchen = Door (address=None, devices=(pi_kitchen), name="Kitchen Window")

pi_frontdoor = StateInterface(RPIInput(11))	#BCM 17
cs_frontdoor = Door (address=None, devices=(pi_frontdoor), name="Front Door")

pi_basementbath = StateInterface(RPIInput(13))	#BCM 27
cs_basementbath = Door (address=None, devices=(pi_basementbath), name="Basement Bathroom Window")

pi_storageroom = StateInterface(RPIInput(15))	#BCM 22
cs_storageroom = Door (address=None, devices=(pi_storageroom), name="Storage Room Window")

pi_familyroom = StateInterface(RPIInput(19))	#BCM 10
cs_familyroom = Door (address=None, devices=(pi_familyroom), name="Family Room Window")

pi_kaitysbed = StateInterface(RPIInput(21))	#BCM 9
cs_kaitysbed = Door (address=None, devices=(pi_kaitysbed), name="Kaity's Bedroom Window")

pi_diningroom = StateInterface(RPIInput(22))	#BCM 25
cs_diningroom = Door (address=None, devices=(pi_diningroom), name="Dining Room Window")

pi_masterbath = StateInterface(RPIInput(23))	#BCM 11
cs_masterbath = Door (address=None, devices=(pi_masterbath), name="Master Bathroom Window")

pi_backdoor = StateInterface(RPIInput(24)) 	#BCM 2
cs_backdoor = Door (address=None, devices=(pi_backdoor), name="Back Door")

pi_hallway = StateInterface(RPIInput(12))	#BCM 18
mt_hallway = Motion (address=None, devices=(pi_hallway), initial=Command.STILL, name="Hallway Motion",	
	mapped=(
		{Attribute.COMMAND: Command.OPEN, Attribute.MAPPED: Command.MOTION},
		{Attribute.COMMAND: Command.CLOSE,Attribute.MAPPED: Command.STILL}
		),
        delay={Attribute.COMMAND: Command.STILL,Attribute.SECS: 30}
        )

#Example of a hardware scene not defined in the PLM
s_masterbath =  Scene('15.64.1D:04', devices=(insteon,), name="Master Bathroom",
    controllers=[Controller(sl_master2)],
    responders = { sl_master2: {'state': State.ON} })

#Example of a hardware scene defined as scene #2 in the PLM    
s_livingroom = Scene(address="00.00.02", devices=(insteon,), update=False, name="Living Room Scene",
    controllers=[Controller(sl_livingroom1)],
    responders={
        ll_livingroom1: {'state': State.ON},
        ll_livingroom2: {'state': State.ON},
        sl_livingroom1: {'state': State.ON}
    })

#Examlpe of a scene defined as scene #3 in the PLM that has no other controllers.    
s_movietime = Scene(address="00.00.03", devices=(insteon,), update=False, name="Movie Scene",
    responders={
        ll_livingroom1: {'state': (State.LEVEL, 127)},
        ll_livingroom2: {'state': (State.LEVEL, 127)},
        sl_livingroom1: {'state': (State.LEVEL, 127)},
        sl_livingroom2: {'state': State.OFF}
    })


#Update Insteon Status
print "Updating status..."
insteon.update_status()

#Update LED status for a KeypadLinc
insteon.command(kl_master1, 'ledstatus')

def MainLoop(*args, **kwargs):
	pass

