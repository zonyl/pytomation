import time
from unittest import TestCase, main
from mock import Mock, PropertyMock, MagicMock
from datetime import datetime

from pytomation.utility.timer import Timer as CTimer
from pytomation.devices import InterfaceDevice, State, StateDevice, Attribute
from pytomation.interfaces import Command, HAInterface

class InterfaceDevice_Tests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        p = PropertyMock(side_effect=ValueError)
        type(self.interface).state = p
        self.device = InterfaceDevice('D1', self.interface)
        
    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'HADevice could not be instantiated')
        
    def test_no_param_init(self):
        d = InterfaceDevice()
        self.assertIsNotNone(d)

    def test_on(self):
        self.device.on()
        self.interface.on.assert_called_with('D1')
        
    def test_substate(self):    
        self.device.command((State.LEVEL, 80))
        self.interface.level.assert_called_with('D1', 80)
    
    def test_read_only(self):
        self.device.read_only(True)
        self.device.on()
        self.assertFalse(self.interface.on.called)

    def test_controlled_devices_no_delay_default(self):
        i = Mock()
        d1 = StateDevice()
        d2 = InterfaceDevice(
                             devices=(i,d1),
                             delay={
                                    Attribute.COMMAND: Command.OFF,
                                    Attribute.SECS: 3
                                    },
                             initial=State.ON,
                             )
        d1.off()
        self.assertEqual(d2.state, State.ON)
        d2.command(command=Command.OFF, source=i)
        self.assertEqual(d2.state, State.OFF)

    def test_time_on(self):
        now = datetime.now()
        hours, mins, secs = now.timetuple()[3:6]
        secs = (secs + 2) % 60
        mins += (secs + 2) / 60
        trigger_time = '{h}:{m}:{s}'.format(
                                             h=hours,
                                             m=mins,
                                             s=secs,
                                                 )
        self.device.time(time=trigger_time, command=Command.ON)
        time.sleep(3)
        self.assertTrue( self.interface.on.called)

    def test_random_sync(self):
        # Should randomly sync state with the objects
        # Usually for X10 devices that do not have an acknowledgement
        self.device.sync = True
        
        device = InterfaceDevice(address='asdf', 
                                 sync=True)
        self.assertIsNotNone(device)
        self.assertTrue(device.sync)
    
    def test_initial(self):
        interface = Mock()
        p = PropertyMock(side_effect=ValueError)
        type(interface).state = p
        device = InterfaceDevice(address='asdf',
                                 devices=interface,
                                 initial=State.ON
                                 )
        interface.on.assert_called_with('asdf')
#        interface.initial.assert_called_with('asdf')
        
        device1 = StateDevice()
        device1.on()
        interface2 = Mock()
        type(interface2).state = p
        device = InterfaceDevice(address='asdf',
                                 devices=interface2,
                                 initial=State.ON
                                 )
        interface2.on.assert_called_with('asdf')
        
    def test_incoming(self):
        i = MagicMock()
        hi = HAInterface(i)
        d = InterfaceDevice(address='asdf',
                             devices=hi)
        hi._onCommand(Command.ON, 'asdf')
        time.sleep(1)
        self.assertEqual(d.state, State.ON)
        
    def test_loop_prevention(self):
        d = InterfaceDevice(
                             devices=(self.interface),
                             delay={Attribute.COMMAND: Command.OFF,
                                    Attribute.SECS: 2}
                             )
        d.on();
        self.interface.on.assert_called_once_with(None)
        d.command(command=Command.OFF, source=self.interface)
        time.sleep(3)
        self.assertFalse(self.interface.off.called)

    def test_no_repeat(self):
        #if the state is already set then dont send the command again
        self.device.off()
        self.assertEqual(self.device.state, State.OFF)
        self.device.on()
        self.assertEqual(self.device.state, State.ON)
        self.interface.on.assert_called_once_with('D1')
        self.interface.on.reset_mock()
        self.device.on()
        self.assertEqual(self.device.state, State.ON)
        self.assertFalse(self.interface.on.called)
        
    def test_interface_interface_source(self):
        pass

if __name__ == '__main__':
    main() 