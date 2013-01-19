
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Door2, State
from pytomation.interfaces import Command

class Door2Tests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        self.interface.state = State.UNKNOWN
        self.device = Door2('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Door Device could not be instantiated')

    def test_door_open(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.command(Command.ON)
        self.assertEqual(self.device.state, State.OPEN)
        
    def test_door_closed(self):
        door = Door2('D1', devices=(self.interface))
#        self.device._on_command('D1', State.ON, self.interface)
        self.device.command(Command.ON)
        self.assertEqual(self.device.state, State.OPEN)
#        self.device._on_command('D1', State.OFF, self.interface)
        self.device.command(Command.OFF)
        self.assertEqual(self.device.state, State.CLOSED)

if __name__ == '__main__':
    main() 