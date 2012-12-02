import time
from unittest import TestCase, main
from mock import Mock
from datetime import datetime

from pytomation.devices import StateDevice, State

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
        print 'Trigger Time' + trigger_time
        self.device.time_on(trigger_time)
        time.sleep(4)
        self.assertEqual(self.device.state, self.device.ON)

    def test_bind_devices(self):
        s2 = StateDevice(self.device)
        self.device.on()
        self.assertIsNotNone(s2)

    def test_bind_devices_initial_state(self):
        s1 = StateDevice()
        self.assertEqual(s1.state, State.UNKNOWN)
        s1.on()
        self.assertEqual(s1.state, State.ON)
        s2 = StateDevice(s1)
        self.assertEqual(s2.state, State.ON)
        s3 = StateDevice(s1, initial_state=State.OFF)
        self.assertEqual(s3.state, State.OFF)
    
    def test_invalid_state(self):
        try:
            self.device.invalid_state()
        except AttributeError, ex:
            return
        except:
            pass
        self.fail('Attribute Exception not raised')

    def test_delay_off(self):
        # After state change, return to off in 2 secs
        self.device.delay_off(2)
        self.device.on()
        time.sleep(1)
        self.assertEqual(self.device.state, State.ON)
        time.sleep(2)
        self.assertEqual(self.device.state, State.OFF)
        
        # re-trigger timer
        self.assertEqual(self.device.state, State.OFF)
        self.device.on()
        self.assertEqual(self.device.state, State.ON)
        time.sleep(1)
        self.assertEqual(self.device.state, State.ON)
        self.device.on()
        time.sleep(1)
        self.assertEqual(self.device.state, State.ON)
        time.sleep(3)
        self.assertEqual(self.device.state, State.OFF)
    
    def test_ignore_state(self):
        s1 = StateDevice()
        s2 = StateDevice(s1)
        s1.on()
        self.assertEqual(s2.state, State.ON)
        s1.off()
        self.assertEqual(s2.state, State.OFF)
        s2.ignore_on()
        s1.on()
        self.assertEqual(s2.state, State.OFF)
        s2.ignore_on(False)
        s1.on()
        self.assertEqual(s2.state, State.ON)
    
    def test_init_extended(self):
        s1 = StateDevice(
                         devices=(self.device),
                         time_off='11:59pm',
                         delay_off=2*60,
                         ignore_dark=True,
                         )
        self.assertIsNotNone(s1)
    
    def tearDown(self):
        self.device = None

if __name__ == '__main__':
    main() 