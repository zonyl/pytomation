
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Motion, State

class MotionTests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        self.interface.state = State.UNKNOWN
        self.device = Motion('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Motion Device could not be instantiated')

    def test_motion_motion(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device._on_command('D1', State.ON)
        self.assertEqual(self.device.state, State.MOTION)
        self.device._on_command('D1', State.OFF)
        self.assertEqual(self.device.state, State.STILL)


if __name__ == '__main__':
    main() 