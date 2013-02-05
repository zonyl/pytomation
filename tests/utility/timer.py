import time

from mock import Mock
from unittest import TestCase, main
from datetime import datetime, timedelta

from pytomation.utility.timer import Timer as CTimer


class TimerTests(TestCase):
    def setUp(self):
        pass

    def test_no_sec_callback(self):
        callback = Mock()
        callback.test.return_value = True
        rt = CTimer()
        rt.interval = 60
        rt.action(callback.test, ())
        rt.start()
        time.sleep(3)
        rt.stop()
        self.assertFalse(callback.test.called)

    def test_3_sec_callback(self):
        callback = Mock()
        callback.test.return_value = True
        rt = CTimer(3)
        rt.action(callback.test, ())
        rt.start()
        self.assertFalse(callback.test.called)
        time.sleep(4)
        self.assertTrue(callback.test.called)

    def test_double_timer_bug(self):
        callback = Mock()
        callback.test.return_value = True
        rt = CTimer(3)
        rt.action(callback.test, ())
        rt.start()
        rt.start()
        rt.stop()
        self.assertFalse(callback.test.called)
        time.sleep(4)
        self.assertFalse(callback.test.called)
        
    def test_isAlive(self):
        rt = CTimer()
        rt.interval = 2
        rt.start()
        self.assertTrue(rt.isAlive())
        time.sleep(3)
        self.assertFalse(rt.isAlive())


if __name__ == '__main__':
    main()