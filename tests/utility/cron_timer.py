import time

from unittest import TestCase, main
from datetime import datetime, timedelta

from pytomation.utility import CronTimer


class CronTimerTests(TestCase):
    def setUp(self):
        self.called = False
        self.ct = CronTimer()

    def test_callback(self):
        datetime.now()
        t = datetime(*datetime.now().timetuple()[:6])
        self.ct.interval(secs=2)
        self.ct.action(self.callback, ())
        self.ct.run()
        time.sleep(3)
        self.assertEqual(self.called, True, "Callback was not called")

    def test_2_sec_intervals(self):
#        self.ct.interval(secs=2,)
        pass

    def callback(self):
        self.called = True

if __name__ == '__main__':
    main()