from datetime import datetime
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Light, Door, Location, State

class LightTests(TestCase):

    def setUp(self):
        self.interface = Mock()
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
        self.device = Light('D1', self.interface, door)
        door.open()
        self.assertTrue(self.interface.on.called)

    def test_location_triggered(self):
        home = Location('35.2269', '-80.8433')
        home.local_time = datetime(2012,6,1,12,0,0)
        light = Light('D1', home)
        self.assertEqual(light.state, State.OFF)
        home.local_time = datetime(2012,6,1,0,0,0)
        self.assertEqual(light.state, State.ON)
        
        
if __name__ == '__main__':
    main() 