from unittest import TestCase

from mock import Mock
from pytomation.interfaces import HAInterface
from pytomation.devices import Thermostat, State


class ThermostatTests(TestCase):
    def setUp(self):
        self.interface = Mock()
        self.device = Thermostat('192.168.1.3', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device)

    def test_cool(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.cool()
        self.assertEqual(self.device.state, State.COOL)
        self.interface.cool.assert_called_with('192.168.1.3')

    def test_heat(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.heat()
        self.assertEqual(self.device.state, State.HEAT)
        self.interface.heat.assert_called_with('192.168.1.3')

    def test_off(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.off()
        self.assertEqual(self.device.state, State.OFF)
        self.interface.off.assert_called_with('192.168.1.3')

    def test_level(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.level(72)
        self.assertEqual(self.device.state, (State.LEVEL, 72))
        self.interface.level.assert_called_with('192.168.1.3', 72)
