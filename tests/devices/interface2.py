import time
from unittest import TestCase, main
from mock import Mock, PropertyMock, MagicMock
from datetime import datetime

from pytomation.utility.timer import Timer as CTimer
from pytomation.devices import Interface2Device, State2, State2Device, Attribute
from pytomation.interfaces import Command, HAInterface

class Interface2Device_Tests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        p = PropertyMock(side_effect=ValueError)
        type(self.interface).state = p
        self.device = Interface2Device('D1', self.interface)
        
    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'HADevice could not be instantiated')
        
    def test_no_param_init(self):
        d = Interface2Device()
        self.assertIsNotNone(d)

    def test_on(self):
        self.device.on()
        self.interface.on.assert_called_with('D1')
        
    def test_substate(self):    
        self.device.command((State2.LEVEL, 80))
        self.interface.level.assert_called_with('D1', 80)
    
    def test_read_only(self):
        self.device.read_only(True)
        self.device.on()
        self.assertFalse(self.interface.on.called)
        
        
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
        
        device = Interface2Device(address='asdf', 
                                 sync=True)
        self.assertIsNotNone(device)
        self.assertTrue(device.sync)
    
    def test_initial(self):
        interface = Mock()
        p = PropertyMock(side_effect=ValueError)
        type(interface).state = p
        device = Interface2Device(address='asdf',
                                 devices=interface,
                                 initial=State2.ON
                                 )
        interface.on.assert_called_with('asdf')
#        interface.initial.assert_called_with('asdf')
        
        device1 = State2Device()
        device1.on()
        interface2 = Mock()
        type(interface2).state = p
        device = Interface2Device(address='asdf',
                                 devices=interface2,
                                 initial=State2.ON
                                 )
        interface2.on.assert_called_with('asdf')
        
    def test_incoming(self):
        i = MagicMock()
        hi = HAInterface(i)
        d = Interface2Device(address='asdf',
                             devices=hi)
        hi._onCommand(Command.ON, 'asdf')
        time.sleep(1)
        self.assertEqual(d.state, State2.ON)
        
    def test_loop_prevention(self):
        d = Interface2Device(
                             devices=(self.interface),
                             delay={Attribute.COMMAND: Command.OFF,
                                    Attribute.SECS: 2}
                             )
        d.on();
        self.interface.on.assert_called_once_with(None)
        d.command(command=Command.OFF, source=self.interface)
        time.sleep(3)
        self.assertFalse(self.interface.off.called)

if __name__ == '__main__':
    main() 