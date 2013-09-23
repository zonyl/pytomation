from unittest import TestCase

from mock import Mock
from pytomation.interfaces import HAInterface
from pytomation.devices import Thermostat, State
from pytomation.interfaces.common import *


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
        
    def test_circulate(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.circulate()
        self.assertEqual(self.device.state, State.CIRCULATE)
        self.interface.circulate.assert_called_with('192.168.1.3')
        
    def test_automatic_mode_for_device_that_does_not(self):
        #Oddly enough the homewerks thermostat doesnt have an auto mode
        self.interface.automatic = None
        self.device.command((Command.LEVEL, 72))
        self.device.command(Command.AUTOMATIC)
        self.device.command(command=(Command.LEVEL, 76), source=self.interface, address='192.168.1.3')
        self.interface.cool.assert_called_with('192.168.1.3')
        self.interface.level.assert_called_with('192.168.1.3', 72)
        assert not self.interface.heat.called
        self.interface.heat.reset_mock()
        self.interface.level.reset_mock()
        self.device.command(command=(Command.LEVEL, 54), source=self.interface, address='192.168.1.3')
        self.interface.heat.assert_called_with('192.168.1.3')
        assert not self.interface.level.called
        # Test that it does not repeat mode setting unnecessarily
        self.interface.heat.reset_mock()
        self.interface.level.reset_mock()
        self.device.command(command=(Command.LEVEL, 58), source=self.interface, address='192.168.1.3')
        assert not self.interface.heat.called
        assert not self.interface.level.called
        self.interface.heat.reset_mock()
        self.interface.cool.reset_mock()
        self.interface.level.reset_mock()
        self.device.command(command=(Command.LEVEL, 98), source=self.interface, address='192.168.1.3')
        self.interface.cool.assert_called_with('192.168.1.3')
        assert not self.interface.heat.called
        assert not self.interface.level.called
        # Test the delta setting
        self.device.automatic_delta(1)
        self.interface.heat.reset_mock()
        self.interface.cool.reset_mock()
        self.interface.level.reset_mock()
        self.device.command(command=(Command.LEVEL, 71), source=self.interface, address='192.168.1.3')
        assert not self.interface.heat.called
        assert not self.interface.level.called
        self.device.command(command=(Command.LEVEL, 70), source=self.interface, address='192.168.1.3')
        self.interface.heat.assert_called_with('192.168.1.3')
        
    def test_automatic_delta(self):
        self.device = Thermostat(
                       address='192.168.1.3',
                       devices=self.interface,
                       automatic_delta=2
                       )
        self.interface.automatic = None
        self.device.command((Command.LEVEL, 72))
        self.interface.level.assert_called_with('192.168.1.3', 72)
        self.interface.level.reset_mock()
        self.device.command(Command.AUTOMATIC)
        self.device.command(command=(Command.LEVEL, 76), source=self.interface, address='192.168.1.3')
        self.interface.cool.assert_called_with('192.168.1.3')
        assert not self.interface.heat.called
        self.interface.heat.reset_mock()
        self.interface.cool.reset_mock()
        self.interface.level.reset_mock()
        self.device.command(command=(Command.LEVEL, 71), source=self.interface, address='192.168.1.3')
        assert not self.interface.heat.called
        
        
    def test_automatic_delta_setpoint_switchover(self):
        self.device = Thermostat(
                       address='a',
                       devices=self.interface,
                       automatic_delta=2
                       )
        self.interface.automatic = None
        self.device.command(command=(Command.LEVEL, 76), source=self.interface, address='a')
        self.device.command((Command.LEVEL, 70))
        # we are not in automatic mode yet
        assert not self.interface.cool.called
        self.device.command(Command.AUTOMATIC)
        self.device.command(command=(Command.LEVEL, 76), source=self.interface, address='a')
        self.interface.cool.assert_called_with('a')
        self.device.command(command=(Command.LEVEL, 71), source=self.interface, address='a')
        self.interface.heat.reset_mock()
        self.interface.cool.reset_mock()
        self.interface.level.reset_mock()
        # reset set point within delta
        self.device.command((Command.LEVEL, 72))
        assert not self.interface.heat.called
        self.device.command(command=(Command.LEVEL, 69), source=self.interface, address='a')
        self.interface.heat.assert_called_with('a')

    def test_hold(self):
        assert not self.interface.hold.called
        self.device.command(Command.HOLD)
        self.interface.hold.assert_called_with('192.168.1.3')
        
        
        
        
        
        
