import time
from unittest import TestCase, main
from mock import Mock
from datetime import datetime

from pytomation.devices import StateDevice

class StateDevice_Tests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        self.device = StateDevice()
        
    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'HADevice could not be instantiated')

    def test_on(self):
        self.assertEqual(self.device.state, self.device.UNKNOWN)
        self.device.on()
        self.assertEqual(self.device.state, self.device.ON)
        
    def test_on_off(self):
        callback_obj = Mock()
        self.device.on_off(callback_obj.callback)
        self.device.off()
        self.assertTrue(callback_obj.callback.called)
        callback_obj.callback.assert_called_once_with(state=self.device.OFF, previous_state=self.device.UNKNOWN, source=self.device)
        
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
        time.sleep(4)
        self.assertEqual(self.device.state, self.device.ON)

    def test_bind_devices(self):
        s2 = StateDevice(self.device)
        self.device.on()
        self.assertIsNotNone(s2)

    def tearDown(self):
        self.device = None

if __name__ == '__main__':
    main() 