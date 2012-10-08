import time

from unittest import TestCase, main
from datetime import datetime, timedelta

from pytomation.utility import CronTimer, AllMatch


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

    def test_datetime_to_cron(self):
        cron = CronTimer.to_cron('5:34pm')
        self.assertEqual(cron[0], 0)
        self.assertEqual(cron[1], 34)
        self.assertEqual(cron[2], 17)
        self.assertEqual(cron[4], AllMatch())

        cron = CronTimer.to_cron('6:52 pm')
        self.assertEqual(cron[0], 0)
        self.assertEqual(cron[1], 52)
        self.assertEqual(cron[2], 18)
        self.assertEqual(cron[4], AllMatch())

        cron = CronTimer.to_cron('5:13 AM')
        self.assertEqual(cron[0], 0)
        self.assertEqual(cron[1], 13)
        self.assertEqual(cron[2], 5)
        self.assertEqual(cron[4], AllMatch())

        cron = CronTimer.to_cron('5:13:34 AM')
        self.assertEqual(cron[0], 34)
        self.assertEqual(cron[1], 13)
        self.assertEqual(cron[2], 5)
        self.assertEqual(cron[4], AllMatch())

        cron = CronTimer.to_cron('3:14')
        self.assertEqual(cron[0], 0)
        self.assertEqual(cron[1], 14)
        self.assertEqual(cron[2], 3)
        self.assertEqual(cron[4], AllMatch())

        cron = CronTimer.to_cron('18:42')
        self.assertEqual(cron[0], 0)
        self.assertEqual(cron[1], 42)
        self.assertEqual(cron[2], 18)
        self.assertEqual(cron[4], AllMatch())

    def callback(self):
        self.called = True

if __name__ == '__main__':
    main()