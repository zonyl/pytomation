import time
from unittest import TestCase, main
from mock import Mock, PropertyMock
from datetime import datetime

from pytomation.utility.timer import Timer as CTimer
from pytomation.devices import InterfaceDevice, State, StateDevice

class InterfaceDevice_Tests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        p = PropertyMock(side_effect=ValueError)
        type(self.interface).state = p
        self.device = InterfaceDevice('D1', self.interface)
        
    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'HADevice could not be instantiated')

    def test_on(self):
        self.device.on()
        self.interface.on.called_with('D1')
                
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
        self.device.time_on(trigger_time)
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
                                 initial_state=State.ON
                                 )
        interface.on.assert_called_with('asdf')
        
        device1 = StateDevice()
        device1.on()
        interface2 = Mock()
        type(interface2).state = p
        device = InterfaceDevice(address='asdf',
                                 devices=interface2,
                                 initial_state=State.ON
                                 )
        interface2.on.assert_called_with('asdf')
        
        

if __name__ == '__main__':
    main() 