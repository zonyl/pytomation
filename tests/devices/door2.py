
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Door2, State2
from pytomation.interfaces import Command

class Door2Tests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        self.interface.state = State2.UNKNOWN
        self.device = Door2('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Door Device could not be instantiated')

    def test_door_open(self):
        self.assertEqual(self.device.state, State2.UNKNOWN)
        self.device.command(Command.ON)
        self.assertEqual(self.device.state, State2.OPEN)
        
    def test_door_closed(self):
        door = Door2('D1', devices=(self.interface))
#        self.device._on_command('D1', State2.ON, self.interface)
        self.device.command(Command.ON)
        self.assertEqual(self.device.state, State2.OPEN)
#        self.device._on_command('D1', State2.OFF, self.interface)
        self.device.command(Command.OFF)
        self.assertEqual(self.device.state, State2.CLOSED)

if __name__ == '__main__':
    main() 