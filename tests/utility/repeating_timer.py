import time

from unittest import TestCase, main
from datetime import datetime, timedelta

from pytomation.utility import RepeatingTimer


class RepeatingTimerTests(TestCase):
    def setUp(self):
        self.called = False

    def test_no_sec_callback(self):
        rt = RepeatingTimer()
        self.called = False
        rt.interval = 60
        rt.action(self.callback, ())
        rt.start()
        time.sleep(3)
        rt.stop()
        self.assertEqual(self.called, False, "Callback was not called")

    def test_1_sec_callback(self):
        rt = RepeatingTimer()
        self.called = False
        rt.interval = 1
        rt.action(self.callback, ())
        rt.start()
        time.sleep(3)
        rt.stop()
        self.assertEqual(self.called, True, "Callback was not called")

    def callback(self, *args, **kwargs):
        self.called = True

if __name__ == '__main__':
    main()