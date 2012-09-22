import time

from unittest import TestCase, main
from datetime import datetime, timedelta

from pytomation.utility import CronTimer


class CronTimerTests(TestCase):
    def setUp(self):
        self.called = False
        self.ct = CronTimer()

    def test_2_sec_callback(self):
        self.called = False
        t = datetime.now().timetuple()[5]
        t += 2
        self.ct.interval(secs=t)
        self.ct.action(self.callback, ())
        self.ct.start()
        time.sleep(3)
        self.ct.stop()
        self.assertEqual(self.called, True, "Callback was not called")

    def test_2_sec_intervals(self):
        self.called = False
        t = datetime.now().timetuple()[5]
        self.ct.interval(secs=(t + 2 % 60, t + 4 % 60))
        self.ct.action(self.callback, ())
        self.ct.start()
        time.sleep(3)
        self.assertEqual(self.called, True, "Callback was not called - 1st iteration")
        self.called = False
        time.sleep(3)
        self.assertEqual(self.called, True, "Callback was not called - 2nd iteration")
        self.ct.stop()

    def callback(self):
        self.called = True

if __name__ == '__main__':
    main()