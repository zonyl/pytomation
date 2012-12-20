from unittest import TestCase

from pytomation.devices import State2Device, State2
from pytomation.interfaces import Command

class State2Tests(TestCase):
    def test_instance(self):
        self.assertIsNotNone(State2Device())

    def test_unknown_initial(self):
        self.assertEqual(State2Device().state, State2.UNKNOWN)

    def test_initial(self):
        device = State2Device(
                        initial=State2.ON
                        )
        self.assertEqual(device.state, State2.ON)
        
    def test_command_on(self):
        device = State2Device()
        self.assertEqual(device.state, State2.UNKNOWN)
        device.on()
        self.assertEqual(device.state, State2.ON)
    
    def test_command_subcommand(self):
        device = State2Device()
        self.assertEqual(device.state, State2.UNKNOWN)
        device.level(80)
        self.assertEqual(device.state, (State2.LEVEL, 80))
    
    
        