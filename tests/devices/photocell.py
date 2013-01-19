
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Photocell2, State
from pytomation.interfaces import Command

class Photocell2Tests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        self.interface.state = State.UNKNOWN
        self.device = Photocell2('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Photocell Device could not be instantiated')

    def test_photocell_state(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.command(Command.DARK)
        self.assertEqual(self.device.state, State.DARK)
        self.device.command(Command.LIGHT)
        self.assertEqual(self.device.state, State.LIGHT)


if __name__ == '__main__':
    main() 