import time

from datetime import datetime
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Light, Door, Location, State, Motion, \
                                Photocell, Attribute, StateDevice
from pytomation.interfaces import Command

class LightTests(TestCase):

    def setUp(self):
        self.interface = Mock()
        self.interface.state = State.UNKNOWN
        self.device = Light('D1', self.interface)

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
        door = Door()
        self.assertIsNotNone(door)
        self.device = Light('D1', devices=(self.interface, door))
        door.open()
        self.assertTrue(self.interface.on.called)
        
    def test_door_closed(self):
        door = Door()
        self.assertIsNotNone(door)
        door.open()
        self.device = Light('D1', devices=(self.interface, door))
#        self.assertTrue(self.interface.initial.called)
        self.assertFalse(self.interface.off.called)
        door.close()
        self.assertTrue(self.interface.off.called)
#        self.interface.on.assert_called_once_with('')
        door.open()
        self.assertTrue(self.interface.on.called)
        
    def test_location_triggered(self):
        home = Location('35.2269', '-80.8433')
        home.local_time = datetime(2012,6,1,12,0,0)
        light = Light('D1', home)
        self.assertEqual(light.state, State.OFF)
        home.local_time = datetime(2012,6,1,0,0,0)
        self.assertEqual(home.state, State.DARK)
        self.assertEqual(light.state, State.ON)
        
    def test_motion_triggered(self):
        motion = Motion('D1', initial=State.STILL)
        self.assertEqual(motion.state, State.STILL)
        light = Light('D1', devices=motion)
        self.assertEqual(light.state, State.OFF)
        motion.motion()
        self.assertEqual(light.state, State.ON)

    def test_photocell_triggered(self):
        photo = Photocell('D1', initial=State.LIGHT)
        light = Light('D1', devices=photo)
        self.assertEquals(light.state, State.OFF)
        photo.dark()
        self.assertEquals(light.state, State.ON)
        
        
    def test_light_restricted(self):
        photo = Photocell('D1', initial=State.LIGHT)
        self.assertEqual(photo.state, State.LIGHT)
        motion = Motion('D1', initial=State.STILL)
        light = Light('D2', devices=(motion, photo),
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
        door = Door()
        self.assertIsNotNone(door)
        light = Light(address='D1', 
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
        motion = Motion()
        light = Light(address='D1', 
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
        motion = Motion()
        motion.still()
        photo = Photocell(address='asdf')
        photo.dark()
        light = Light(address='e3',
                      devices=(photo, motion),
                      initial=photo,
                      )
        self.assertEqual(light.state, State.ON)
        
    def test_light_photocell_delay(self):
        ## Dont like this behavior anymore
        # Delay off should not trigger when photocell tells us to go dark.
        # Do it immediately
#        photo = Photocell()
#        photo.dark()
#        light = Light(address='e3',
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
        light = Light('a2',
                      time={
                            'command': Command.OFF,
                            'time':(0, 30, range(0,5), 0, 0)
                            })
        self.assertIsNotNone(light)
        
        
    def test_light_scenario1(self):
        m = Motion()
        l = Light(
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
        d = Door()
        p = Photocell()
        p.light()
        l =  Light(address='xx.xx.xx', 
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
        m = Motion()
        l = Light(
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
        
    def test_scenario_g2(self):
        d = StateDevice()
        l = Light(address='1E.39.5C', 
               devices=(d),
               delay={
                   Attribute.COMMAND: Command.OFF,
                   Attribute.SECS: 2
                   },
               name='Stair Lights up')
        self.assertEqual(l.state, State.UNKNOWN)
        l.off()
        time.sleep(3)
        self.assertEqual(l.state, State.OFF)
        l.on()
        self.assertEqual(l.state, State.ON)
    
    def test_delay_non_native_command(self):
        m = Motion()
        l = Light(
                  devices=m,
                  delay={
                         Attribute.COMMAND: Command.STILL,
                         Attribute.SECS: 2,
                         },
                  initial=State.ON
                  )
        self.assertEqual(l.state, State.ON)
        m.still()
        self.assertEqual(l.state, State.ON)
        time.sleep(3)
        self.assertEqual(l.state, State.OFF)
        
    def test_light_scenario_g3(self):
        m1 = Motion()
        m2 = Motion()
        l = Light(
                devices=(m1, m2),
                    ignore={
                          Attribute.COMMAND: Command.STILL,
                          },
                    trigger=(
                         {
                           Attribute.COMMAND: Command.MOTION,
                           Attribute.MAPPED: Command.OFF,
                           Attribute.SOURCE: m1,
                           Attribute.SECS: 10
                           },
                           {
                           Attribute.COMMAND: Command.MOTION,
                           Attribute.MAPPED: Command.OFF,
                           Attribute.SOURCE: m2,
                           Attribute.SECS: 2
                            }
                         ),
                  initial=State.OFF,
                  )
        self.assertEqual(l.state, State.OFF)
        m1.motion()
        self.assertEqual(l.state, State.ON)
        # call still just to add some noise. Should be ignored
        m1.still()
        self.assertEqual(l.state, State.ON)
        time.sleep(2)
        # Light should still be on < 10 secs
        self.assertEqual(l.state, State.ON)
        
        m2.motion()
        self.assertEqual(l.state, State.ON)
        # more noise to try and force an issue. Should be ignored
        m2.still()
        m1.still()
        self.assertEqual(l.state, State.ON)
        time.sleep(3)
        # total of 5 secs have elapsed since m1 and 3 since m2
        # Light should be off as m2 set the new time to only 2 secs
        self.assertEqual(l.state, State.OFF)
        
        
if __name__ == '__main__':
    main() 