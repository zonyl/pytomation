import time

from datetime import datetime
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Light2, Door2, Location2, State2, Motion2, \
                                Photocell2
from pytomation.interfaces import Command

class Light2Tests(TestCase):

    def setUp(self):
        self.interface = Mock()
        self.interface.state = State2.UNKNOWN
        self.device = Light2('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Light Device could not be instantiated')

    def test_on(self):
        self.assertEqual(self.device.state, State2.UNKNOWN)
        self.device.on()
        self.assertEqual(self.device.state, State2.ON)
        self.assertTrue(self.interface.on.called)

    def test_on_time(self):
        pass
    
    def test_door_triggered(self):
        door = Door2()
        self.assertIsNotNone(door)
        self.device = Light2('D1', devices=(self.interface, door))
        door.on()
        self.assertTrue(self.interface.on.called)
        
    def test_door_closed(self):
        door = Door2()
        self.assertIsNotNone(door)
        door.on()
        self.device = Light2('D1', devices=(self.interface, door))
        self.assertTrue(self.interface.initial.called)
        self.assertFalse(self.interface.off.called)
        door.off()
        self.assertTrue(self.interface.off.called)
#        self.interface.on.assert_called_once_with('')
        door.on()
        self.assertTrue(self.interface.on.called)
        
    def test_location_triggered(self):
        home = Location2('35.2269', '-80.8433')
        home.local_time = datetime(2012,6,1,12,0,0)
        light = Light2('D1', home)
        self.assertEqual(light.state, State2.OFF)
        home.local_time = datetime(2012,6,1,0,0,0)
        self.assertEqual(home.state, State2.DARK)
        self.assertEqual(light.state, State2.ON)
        
    def test_motion_triggered(self):
        motion = Motion2('D1', initial_state=State2.STILL)
        self.assertEqual(motion.state, State2.STILL)
        light = Light2('D1', motion)
        self.assertEqual(light.state, State2.OFF)
        motion.on()
        self.assertEqual(light.state, State2.ON)

    def test_photocell_triggered(self):
        photo = Photocell2('D1', initial=State2.LIGHT)
        light = Light2('D1', photo)
        self.assertEquals(light.state, State2.OFF)
        photo.on()
        self.assertEquals(light.state, State2.ON)
        
        
    def test_light_restricted(self):
        photo = Photocell2('D1', initial=State2.LIGHT)
        motion = Motion2('D1', initial=State2.STILL)
        light = Light2('D2', (motion, photo))
        self.assertEqual(light.state, State2.OFF)
        motion.on()
        self.assertEqual(light.state, State2.OFF)
        photo.on()
        self.assertEqual(light.state, State2.ON)
        light.off()
        self.assertEqual(light.state, State2.OFF)
        motion.on()
        self.assertEqual(light.state, State2.ON)

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
        door.on()
        self.assertEqual(light.state, State2.ON)
        door.off()
        self.assertEqual(light.state, State2.ON)
        time.sleep(2)
        self.assertEqual(light.state, State2.ON)
        time.sleep(2)
        self.assertEqual(light.state, State2.OFF)

        # Check to see if we can immediately and directly still turn off
        light.off()
        door.on()
        self.assertEqual(light.state, State2.ON)
        light.off()
        self.assertEqual(light.state, State2.OFF)

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
                               'command': Command.OFF,
                               'source': motion,
                               }
                       )
        motion.on()
        self.assertEqual(light.state, State2.ON)
        time.sleep(2)
        motion.off()
        self.assertEqual(light.state, State2.ON)
        time.sleep(1)
        self.assertEqual(light.state, State2.OFF)

    def test_light_photocell_intial(self):
        motion = Motion2()
        motion.off()
        photo = Photocell2(address='asdf')
        photo.on()
        light = Light2(address='e3',
                      devices=(photo, motion),
                      initial=photo,
                      )
        self.assertEqual(light.state, State2.ON)
        
    def test_light_photocell_delay(self):
        # Delay off should not trigger when photocell tells us to go dark.
        # Do it immediately
        photo = Photocell2()
        photo.on()
        light = Light2(address='e3',
                      devices=photo,
                      delay={
                             'command': Command.OFF,
                             'secs': 3
                             })
        self.assertEqual(light.state, State2.ON)
        photo.off()
        self.assertEqual(light.state, State2.OFF)
        
    def test_level(self):
        self.device.command((Command.LEVEL, 40))
        self.assertTrue(self.interface.level.called)

    def test_time_cron(self):
        light = Light2('a2',
                      time={
                            'command': Command.OFF,
                            'time':(0, 30, range(0,5), 0, 0)
                            })
        self.assertIsNotNone(light)

if __name__ == '__main__':
    main() 