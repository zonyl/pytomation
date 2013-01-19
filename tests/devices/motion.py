
from unittest import TestCase, main
from mock import Mock, MagicMock

from pytomation.devices import Motion2, State2
from pytomation.interfaces import Command

class MotionTests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        self.interface.state = State2.UNKNOWN
        self.device = Motion2('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Motion Device could not be instantiated')

    def test_motion_motion(self):
        self.assertEqual(self.device.state, State2.UNKNOWN)
        self.device.command(Command.MOTION, source=self.interface)
#        self.device._on_command('D1', State2.ON)
        self.assertEqual(self.device.state, State2.MOTION)
#        self.device._on_command('D1', State2.OFF)
        self.device.command(Command.STILL, source=self.interface)
        self.assertEqual(self.device.state, State2.STILL)

    def test_motion_ignore(self):
        self.device = Motion2('D1', devices=(self.interface), ignore={
                                                                      'command': Command.STILL,
                                                                      },
                              )
        self.device.command(Command.MOTION, source=self.interface)
#        self.device._on_command('D1', State2.ON, self.interface)
        self.assertEqual(self.device.state, State2.MOTION)
        self.device.command(Command.MOTION, source=self.interface)
#        self.device._on_command('D1', State2.OFF, self.interface)
        self.assertEqual(self.device.state, State2.MOTION)
        
    def test_motion_on(self):
        m = Motion2()
        m.command(command=Command.ON, source=None)
        self.assertEqual(m.state, State2.MOTION)        

if __name__ == '__main__':
    main() 