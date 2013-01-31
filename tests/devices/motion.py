
from unittest import TestCase, main
from mock import Mock, MagicMock
import time

from pytomation.devices import Motion, State, Attribute
from pytomation.interfaces import Command

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
        self.device.command(Command.MOTION, source=self.interface)
#        self.device._on_command('D1', State.ON)
        self.assertEqual(self.device.state, State.MOTION)
#        self.device._on_command('D1', State.OFF)
        self.device.command(Command.STILL, source=self.interface)
        self.assertEqual(self.device.state, State.STILL)

    def test_motion_ignore(self):
        self.device = Motion('D1', devices=(self.interface), ignore={
                                                                      'command': Command.STILL,
                                                                      },
                              )
        self.device.command(Command.MOTION, source=self.interface)
#        self.device._on_command('D1', State.ON, self.interface)
        self.assertEqual(self.device.state, State.MOTION)
        self.device.command(Command.MOTION, source=self.interface)
#        self.device._on_command('D1', State.OFF, self.interface)
        self.assertEqual(self.device.state, State.MOTION)
        
    def test_motion_on(self):
        m = Motion()
        m.command(command=Command.ON, source=None)
        self.assertEqual(m.state, State.MOTION)        

    def test_motion_delay_from_interface(self):
        i = Mock()
        m = Motion(devices=i,
                   delay={
                          Attribute.COMMAND: Command.STILL,
                          Attribute.SECS: 2,
                          })
        m.command(command=Command.MOTION, source=i)
        self.assertEqual(m.state, State.MOTION)
        m.command(command=Command.STILL, source=i)
        self.assertEqual(m.state, State.MOTION)
        time.sleep(3)
        self.assertEqual(m.state, State.STILL)
        

if __name__ == '__main__':
    main() 