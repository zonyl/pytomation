import select
import time

from pytomation.interfaces import Serial, W800rf32, InsteonPLM, Wtdio, NamedPipe, \
                                StateInterface, Command, HTTPServer
from pytomation.devices import Motion, Door, Light, Location, InterfaceDevice, Room, \
                                Photocell, Generic, StateDevice, State, Attribute


###################### INTERFACE CONFIG #########################
web = HTTPServer()

insteon = InsteonPLM(Serial('/dev/ttyR2', 19200, xonxoff=False))
wtdio = Wtdio(Serial('/dev/mh_weeder_port', 9600))
w800 = W800rf32(Serial('/dev/mh_w800_port', 4800, xonxoff=False))

# Set the I/O points as inputs on the wtdio board, these are all set as inputs
wtdio.setChannel('ASA')
wtdio.setChannel('ASB')
wtdio.setChannel('ASC')
wtdio.setChannel('ASD')
wtdio.setChannel('ASE')
wtdio.setChannel('ASF')
wtdio.setChannel('ASG')

#wtdio.dio_invert('G')

###################### DEVICE CONFIG #########################

# ______ REMOTES ____________________________________________________ 

# X10 Slimline RF wall switch in living room
sl_sofa = Generic('A1', w800, name='Sofa Switch')
sl_stereo = Generic('A2', w800, name='Stereo Switch')
sl_outside = Generic('A3', w800, name='Outside Switch')
sl_xmas = Generic('A0', w800, name='Xmas Switch')

# X10 Slimline RF wall switch in Recroom
sl_recroom_light = Generic('D1', w800, name='Recroom Light Switch')
sl_recroom_lamp = Generic('D2', w800, name='Recroom Lamp Switch')
sl_recroom_tree = Generic('D3', w800, name='Recroom Tree Switch')
sl_alloff = Generic('D0', w800, name='Recroom all off')


# HR12A - X10 Powerhouse Palmpad in living room
pp_sofa = Generic('B1', w800, name='Sofa Pad')
pp_buffet = Generic('B2', w800, name='Buffet Pad')
pp_piano = Generic('B3', w800, name='Piano Pad')
pp_stereo = Generic('B4', w800, name='Stereo Pad')
pp_bedroom = Generic('B5', w800, name='Bedroom Pad')
pp_bathroom = Generic('B6', w800, name='Bathroom Pad')
pp_fireplace = Generic('B7', w800, name='Fireplace Pad')
pp_xmas = Generic('B8', w800, name='Xmas Pad')

pp_sofa60 = Generic('B9', w800)
pp_scene1 = Generic('B10', w800)
pp_rroom = Generic('B11', w800)



# KC674 - X10 Powerhouse keychain in bedroom
bedroom_onoff = Generic('G1', w800, name='Bedroom Remote')
all_lights = Generic('G2', w800)

#'D1' slimeline downstairs

# KR22A X10 4 button remote - low range
x1 = Generic('E1', w800, name='X1')
x2 = Generic('E2', w800)
x3 = Generic('E3', w800)
x4 = Generic('E4', w800)



# ______ MOTION SENSORS _____________________________________________ 

m_kitchen = Motion(address='AC', devices=wtdio, name='Kitchen Motion')
m_laundry = Motion(address='AD', devices=wtdio, name='Laundry Room Motion')
m_hallway = Motion(address='AE', devices=wtdio, name='Hallway Motion')

# Don't allow this to trigger ON again for 20 seconds
m_stairs  = Motion(address='H1', devices=w800, 
        retrigger_delay = {
            Attribute.SECS: 20    
        },
        name='Stair Motion')
m_recroom = Motion(address='I1', devices=w800, name='Recroom Motion')
m_backdoor = Motion(address='J1', devices=w800, name='Backdoor Motion')



# ______ DOOR CONTACTS ______________________________________________ 
d_back = Door(address='AG', devices=wtdio, name='Backdoor Contact')



# ______ LOCATION ___________________________________________________ 
#
ph_standard = Location('48.9008', '-119.8463',      #moved this east a bit
                       tz='America/Vancouver',
                       mode=Location.MODE.STANDARD, 
                       is_dst=True,
                       name='Standard Photocell')



# ______ GENERICS ___________________________________________________ 
#
# Use this for a oneshot at dark.  
on_at_night = Generic(devices=ph_standard, 
                    ignore=({Attribute.COMMAND: Command.LIGHT}), 
                    name='Dark oneshot')

# Cheap way to say some one is in the house
# Make sure the signal lasts at least one loop through mainloop, my mainloop
# is set to 30 seconds
home = Generic(devices=(m_kitchen,m_stairs,m_hallway),
                delay={ Attribute.COMMAND: Command.STILL, Attribute.SECS: 40 },
                name='Someone is home')


            
# ______ HALLWAY ____________________________________________________ 

# LampLinc
l_piano = Light(address='0E.7C.6C', 
            devices=(insteon, sl_sofa, sl_xmas, ph_standard, pp_piano, all_lights),
            time={
                Attribute.TIME: '10:25pm',
                Attribute.COMMAND: Command.OFF
            },
            name='Piano Lamp')

# Turn on the hallway light at night when the back door is opened then go back
# to previous level 2 minutes later
# Don't turn it on when it's DARK
# This device has additional code in mainloop to handle PREVIOUS levels
# SwitchLinc 2476D V5.4
l_hallway =  Light(address='17.C0.7C', 
            devices=(insteon, ph_standard, d_back, all_lights),
            ignore=({Attribute.COMMAND: Command.DARK}),
            mapped={
                Attribute.COMMAND: (Command.CLOSE),
                Attribute.MAPPED: (Command.PREVIOUS),
                Attribute.SECS: 2*60,
            },
            time={
                Attribute.TIME: '10:20pm',
                Attribute.COMMAND: Command.OFF
            },
            name="Hallway Lights",)


# ______ LIVING ROOM ________________________________________________ 

# LampLinc
# Additional rule in mainloop
l_sofa = Light(address='12.07.1F', 
            devices=(insteon, sl_sofa, pp_sofa, pp_sofa60, all_lights, web),
            send_always=True,
            mapped={
                Attribute.COMMAND: Command.ON,
                Attribute.MAPPED:  (Command.LEVEL, 60),
                Attribute.SOURCE:  pp_sofa60,
            },
            time=({
                Attribute.TIME: '10:00pm',
                Attribute.COMMAND: (Command.LEVEL, 60)
            },
            {
                Attribute.TIME: '10:20pm',
                Attribute.COMMAND: Command.OFF
            },),
            name='Sofa Lamps')

# LampLinc
l_buffet = Light(address='0F.81.88', 
            devices=(insteon, sl_sofa, sl_xmas, pp_buffet, on_at_night, all_lights),
            send_always=True,
            time={
                Attribute.TIME: '10:20pm',
                Attribute.COMMAND: Command.OFF
            },
            name='Buffet Lamp')

# LampLinc
l_fireplace = Light(address='12.06.58', 
            devices=(insteon, sl_xmas, sl_sofa, on_at_night, pp_fireplace, all_lights),
            send_always=True,
            time={
                Attribute.TIME: '10:30pm',
                Attribute.COMMAND: Command.OFF
            },
            name='Fireplace Lamp')

# LampLinc
l_stereo = Light(address='12.09.02', 
            devices=(insteon,sl_stereo, sl_xmas, pp_stereo, all_lights),
            send_always=True,
            time={
                Attribute.TIME: '10:19pm',
                Attribute.COMMAND: Command.OFF
            },
            name='Stereo Lamp')


# ______ BEDROOM ROOM _______________________________________________ 
#SwitchLinc
l_bedroom = Light(address='1A.58.E8', 
            devices=(insteon, bedroom_onoff,pp_bedroom),
            send_always=True,
            name='Master Bedroom Light')


# ______ BATHROOM UP ________________________________________________ 
#SwitchLinc dim v4.35
l_bathroom = Light(address='12.20.B0', 
            devices=(insteon,pp_bathroom, all_lights),
            send_always=True,
            name='Bathroom Lights')

# ______ STAIRS _____________________________________________________ 

# This has 2 motion detectors one at the top of the stairs and one in the 
# Laundry room at the bottom.  Go to the top of the stairs and the light 
# turns on, don't go down, it turns off 15 seconds later.  Go down and laundry
# motion keeps it on while in the room, come up the stairs and the laundry 
# timers cancels and the 15 second time turns off the light.  Nice!
#SwitchLinc 2477S V6.0
l_stair_up = Light(address='1E.39.5C', 
            devices=(insteon, m_stairs, m_laundry),
            trigger=({
                'command': Command.ON,
                'mapped': Command.OFF,
                'source': m_stairs,
                'secs': 15,
            }, {
                'command': Command.ON,
                'mapped': Command.OFF,
                'source': m_laundry,
                'secs': 3*60,
            },),
            ignore={
                'command': Command.STILL,
            },
            name='Stair Lights up')
        


#SwitchLinc 2477S V6.2 Dualband
l_stair_down = Light(address='1F.A9.86', 
            devices=(insteon),
            name='Stairs Lights Down')



# ______ RECROOM ____________________________________________________ 

# LampLinc
l_recroom_lamp = Light(address='18.A1.D3', 
            devices=(insteon, sl_recroom_lamp, m_recroom),
            send_always=True,
            delay={
                Attribute.COMMAND: Command.STILL,
                Attribute.SECS: 5*60
            },
            name='Recroom Lamp')

#SwitchLinc Relay V5.2
l_recroom_light = Light(address='12.DB.5D', 
            devices=(insteon, sl_recroom_light,pp_rroom),
            send_always=True,
            time={
                Attribute.TIME: '10:19pm',
                Attribute.COMMAND: Command.OFF
            },
            name='Recroom Light')



# ______ BATHROOM DOWN ______________________________________________ 

#SwitchLinc Relay
f_bathroom = Light(address='12.E3.54',devices=(insteon),
            mapped={
                Attribute.COMMAND: Command.ON,
                Attribute.MAPPED:  Command.OFF,
                Attribute.SECS: 10*60
            },
            name="Downstairs Bathroom Fan")



# ______ OUTSIDE _______________________________________________ 

#SwitchLinc
l_carport = Light(address='0F.45.9F', 
            devices=(insteon, sl_xmas, ph_standard, m_backdoor),
            # don't come on when dark but restrict until dark
            ignore={Attribute.COMMAND: Command.DARK},  
            send_always=True,
            trigger={
                    Attribute.COMMAND: Command.ON,
                    Attribute.MAPPED: Command.OFF,
                    Attribute.SOURCE: m_backdoor,
                    Attribute.SECS: 3*60,
            },
            time={
                Attribute.TIME: '10:10pm',
                Attribute.COMMAND: Command.OFF
            },
            name='Carport Lights')


#KeypadLinc
# On at sunset, drop back to 40% 60 seconds later
# Door open or motion, light at 100%, then idle
# Light off at 10:30 
l_backdoor = Light(address='12.B8.73', 
            devices=(insteon, sl_outside, ph_standard, d_back, all_lights, m_backdoor),
            send_always=True,
#            ignore=({Attribute.COMMAND: Command.DARK},
            ignore=({Attribute.COMMAND: Command.CLOSE},),
            idle={
                    Attribute.MAPPED:(Command.LEVEL, 40),
                    Attribute.SECS: 60,
            },
            time={
                Attribute.TIME: '10:30pm',
                Attribute.COMMAND: Command.OFF
            },
            name='Backdoor Light')



print "Current daylight state is -> ", ph_standard.state
print "Updating status..."
insteon.update_status()

# My mainloop is set at 30 seconds
def MainLoop(startup=False,*args, **kwargs):

    if startup:
        global ticcount
        global sofaOn
        
        ticcount = 0
        sofaOn = True
        print "Startup..."

    ticcount += 1   # right now every 30 seconds

    # cheap occupancy detector
    if (home.state == State.MOTION):
        ticcount = 0

    if ph_standard.state == State.DARK and d_back.state == State.OPEN:
        if ticcount > 180:   # hour and a half
            l_sofa.on()
            ticcount = 0

    # Turn the sofa light on only if we are home and it's dark
    if ph_standard.state == State.DARK and home.state == State.MOTION and sofaOn:
        l_sofa.on()
        sofaOn = False
    elif ph_standard.state == State.LIGHT:
        sofaOn = True

    htime = time.strftime('%H%M')
    if ph_standard.state == "dark" and htime <= '2230':
        l_hallway._previous_state = (State.LEVEL,40)
    else:
        l_hallway._previous_state = (State.LEVEL, 0)
        

    # Sometimes I run from console and print stuff while testing.
        
    #print "Recroom Lamp   -> ", l_recroom_lamp.state
    #print "Recroom Light  -> ", l_recroom_light.state
    print (time.strftime('%H:%M:%S'))
    #print "Ticcount ----> ", ticcount
    #print "Here --------> ", here.state
    #print "Bathroom Light -> ", l_bathroom.state
    print "Hallway Light  -> ", l_hallway.state
    #print "Carport outlet -> ", l_carport.state
    #print "Bedroom Light  -> ", l_bedroom.state
    #print "Stair Light    -> ", l_stair_up.state
    #print "Test Light     -> ", test.state
    #print "Spin Time -> ",insteon.spinTime
    print "Status Request -> ",insteon.statusRequest
    print '--------------------------'
    
