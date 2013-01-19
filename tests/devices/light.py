import time

from datetime import datetime
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Light2, Door2, Location2, State, Motion2, \
                                Photocell2, Attribute
from pytomation.interfaces import Command

class Light2Tests(TestCase):

    def setUp(self):
        self.interface = Mock()
        self.interface.state = State.UNKNOWN
        self.device = Light2('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Light Device could not be instantiated')

    def test_on(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.on()
        self.assertEqual(self.device.state, State.ON)
        self.assertTrue(self.interface.on.called)

    def test_on_time(self):
        pass
    
    def test_door_triggered(self):
        door = Door2()
        self.assertIsNotNone(door)
        self.device = Light2('D1', devices=(self.interface, door))
        door.open()
        self.assertTrue(self.interface.on.called)
        
    def test_door_closed(self):
        door = Door2()
        self.assertIsNotNone(door)
        door.open()
        self.device = Light2('D1', devices=(self.interface, door))
#        self.assertTrue(self.interface.initial.called)
        self.assertFalse(self.interface.off.called)
        door.close()
        self.assertTrue(self.interface.off.called)
#        self.interface.on.assert_called_once_with('')
        door.open()
        self.assertTrue(self.interface.on.called)
        
    def test_location_triggered(self):
        home = Location2('35.2269', '-80.8433')
        home.local_time = datetime(2012,6,1,12,0,0)
        light = Light2('D1', home)
        self.assertEqual(light.state, State.OFF)
        home.local_time = datetime(2012,6,1,0,0,0)
        self.assertEqual(home.state, State.DARK)
        self.assertEqual(light.state, State.ON)
        
    def test_motion_triggered(self):
        motion = Motion2('D1', initial=State.STILL)
        self.assertEqual(motion.state, State.STILL)
        light = Light2('D1', devices=motion)
        self.assertEqual(light.state, State.OFF)
        motion.motion()
        self.assertEqual(light.state, State.ON)

    def test_photocell_triggered(self):
        photo = Photocell2('D1', initial=State.LIGHT)
        light = Light2('D1', devices=photo)
        self.assertEquals(light.state, State.OFF)
        photo.dark()
        self.assertEquals(light.state, State.ON)
        
        
    def test_light_restricted(self):
        photo = Photocell2('D1', initial=State.LIGHT)
        self.assertEqual(photo.state, State.LIGHT)
        motion = Motion2('D1', initial=State.STILL)
        light = Light2('D2', devices=(motion, photo),
                       initial=photo)
        self.assertEqual(light.state, State.OFF)
        motion.motion()
        self.assertEqual(light.state, State.OFF)
        photo.dark()
        self.assertEqual(light.state, State.ON)
        light.off()
        self.assertEqual(light.state, State.OFF)
        motion.motion()
        self.assertEqual(light.state, State.ON)

    def test_delay_normal(self):
        # Door Open events retrigger delay
        # Instead of turning off in 2 secs should be 4
        door = Door2()
        self.assertIsNotNone(door)
        light = Light2(address='D1', 
                      devices=(self.interface, door),
                      delay={
                             'command': Command.OFF,
                             'secs': 3,
                             'source': door}
                       )
        door.open()
        self.assertEqual(light.state, State.ON)
        door.close()
        self.assertEqual(light.state, State.ON)
        time.sleep(2)
        self.assertEqual(light.state, State.ON)
        time.sleep(2)
        self.assertEqual(light.state, State.OFF)

        # Check to see if we can immediately and directly still turn off
        light.off()
        door.open()
        self.assertEqual(light.state, State.ON)
        light.off()
        self.assertEqual(light.state, State.OFF)

    def test_delay_light_specific(self):
        # motion.off and Photocell.Light events do not retrigger
        motion = Motion2()
        light = Light2(address='D1', 
                      devices=(self.interface, motion),
                      trigger={
                             'command': Command.ON,
                             'mapped': Command.OFF,
                             'secs': 3,
                             },
                       ignore={
                               'command': Command.STILL,
                               'source': motion,
                               }
                       )
        motion.motion()
        self.assertEqual(light.state, State.ON)
        time.sleep(2)
        motion.still()
        self.assertEqual(light.state, State.ON)
        time.sleep(1)
        self.assertEqual(light.state, State.OFF)

    def test_light_photocell_intial(self):
        motion = Motion2()
        motion.still()
        photo = Photocell2(address='asdf')
        photo.dark()
        light = Light2(address='e3',
                      devices=(photo, motion),
                      initial=photo,
                      )
        self.assertEqual(light.state, State.ON)
        
    def test_light_photocell_delay(self):
        ## Dont like this behavior anymore
        # Delay off should not trigger when photocell tells us to go dark.
        # Do it immediately
#        photo = Photocell2()
#        photo.dark()
#        light = Light2(address='e3',
#                      devices=photo,
#                      delay={
#                             'command': Command.OFF,
#                             'secs': 3
#                             })
#        self.assertEqual(light.state, State.ON)
#        photo.light()
#        self.assertEqual(light.state, State.OFF)
        pass
    
    def test_level(self):
        self.device.command((Command.LEVEL, 40))
        self.interface.level.assert_called_with('D1', 40)

    def test_time_cron(self):
        light = Light2('a2',
                      time={
                            'command': Command.OFF,
                            'time':(0, 30, range(0,5), 0, 0)
                            })
        self.assertIsNotNone(light)
        
        
    def test_light_scenario1(self):
        m = Motion2()
        l = Light2(
                address=(49, 6), 
                devices=m,
                mapped={
                        Attribute.COMMAND: Command.MOTION,
                        Attribute.SECS: 30*60
                        },
                ignore=({
                        Attribute.COMMAND: Command.STILL
                        },
                        {
                        Attribute.COMMAND: Command.DARK
                        },
                    ),
                name='Lamp',
                )
        self.assertEqual(l.state, State.UNKNOWN)
        m.command(command=State.ON, source=None)
        self.assertEqual(l.state, State.UNKNOWN)
    
    def test_light_scenario_g1(self):
        d = Door2()
        p = Photocell2()
        p.light()
        l =  Light2(address='xx.xx.xx', 
            devices=(d, p),
            mapped={
               Attribute.COMMAND: (Command.CLOSE),
               Attribute.MAPPED: Command.OFF,
               Attribute.SECS: 2,
            },
            ignore=({Attribute.COMMAND: Command.DARK}),
            name="Hallway Lights",)
        l.on()
        self.assertEqual(l.state, State.ON)
        d.close()
        self.assertEqual(l.state, State.ON)
        time.sleep(3)
        self.assertEqual(l.state, State.OFF)
        d.open()
        self.assertEqual(l.state, State.OFF)
        
        
    def test_light_scenario_2(self):
        m = Motion2()
        l = Light2(
                address=(49, 3),
                devices=(m),
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
                         Attribute.SECS: 2,
                         },
         name='Foyer Light',
                )
        l.off()
        self.assertEqual(l.state, State.OFF)
        m.motion()
        self.assertEqual(l.state, State.OFF)
        time.sleep(3)
        self.assertEqual(l.state, State.OFF)
        
        
        
if __name__ == '__main__':
    main() 