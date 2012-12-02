import time

from datetime import datetime
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Light, Door, Location, State, Motion, \
                                Photocell

class LightTests(TestCase):

    def setUp(self):
        self.interface = Mock()
        self.interface.state = State.UNKNOWN
        self.device = Light('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Light Device could not be instantiated')

    def test_on(self):
        self.assertEqual(self.device.state, self.device.UNKNOWN)
        self.device.on()
        self.assertEqual(self.device.state, self.device.ON)
        self.assertTrue(self.interface.on.called)

    def test_on_time(self):
        pass
    
    def test_door_triggered(self):
        door = Door()
        self.assertIsNotNone(door)
        self.device = Light('D1', (self.interface, door))
        door.open()
        self.assertTrue(self.interface.on.called)
        
    def test_door_closed(self):
        door = Door()
        self.assertIsNotNone(door)
        door.open()
        self.device = Light('D1', (self.interface, door))
        door.closed()
        self.assertFalse(self.interface.on.called)
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
        motion = Motion('D1', initial_state=State.STILL)
        self.assertEqual(motion.state, State.STILL)
        light = Light('D1', motion)
        self.assertEqual(light.state, State.OFF)
        motion.motion()
        self.assertEqual(light.state, State.ON)

    def test_photocell_triggered(self):
        photo = Photocell('D1', initial_state=State.LIGHT)
        light = Light('D1', photo)
        self.assertEquals(light.state, State.OFF)
        photo.dark()
        self.assertEquals(light.state, State.ON)
        
        
    def test_light_restricted(self):
        photo = Photocell('D1', initial_state=State.LIGHT)
        motion = Motion('D1', initial_state=State.STILL)
        light = Light('D2', (motion, photo))
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
                      delay_off=3)
        door.open()
        self.assertEqual(light.state, State.ON)
        door.closed()
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
        # Motion.Still and Photocell.Light events do not retrigger
        motion = Motion()
        light = Light(address='D1', 
                      devices=(self.interface, motion),
                      delay_off=3)
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
                      initial_state=photo,
                      )
        self.assertEqual(light.state, State.ON)
        
    def test_light_photocell_delay(self):
        # Delay off should not trigger when photocell tells us to go dark.
        # Do it immediately
        photo = Photocell()
        photo.dark()
        light = Light(address='e3',
                      devices=photo,
                      delay_off=3)
        self.assertEqual(light.state, State.ON)
        photo.light()
        self.assertEqual(light.state, State.OFF)
        
        


if __name__ == '__main__':
    main() 