
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Photocell, State

class PhotocellTests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        self.interface.state = State.UNKNOWN
        self.device = Photocell('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Photocell Device could not be instantiated')

    def test_photocell_state(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device._on_command('D1', State.ON)
        self.assertEqual(self.device.state, State.DARK)
        self.device._on_command('D1', State.OFF)
        self.assertEqual(self.device.state, State.LIGHT)


if __name__ == '__main__':
    main() 