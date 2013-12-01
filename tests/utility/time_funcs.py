from unittest import TestCase
from pytomation.utility import CronTimer
from pytomation.utility.time_funcs import *

class TimeFuncsTests(TestCase):
    def setUp(self):
        pass
        
    def test_timefuncs_in_range(self):
        start = CronTimer.to_cron("4:52pm")
        end = CronTimer.to_cron("4:55pm")
        now = CronTimer.to_cron("4:54pm")
        self.assertTrue(crontime_in_range(now, start, end))
        
    def test_timefuncs_out_range(self):
        start = CronTimer.to_cron("4:52pm")
        end = CronTimer.to_cron("4:55pm")
        now = CronTimer.to_cron("5:54pm")
        self.assertFalse(crontime_in_range(now, start, end))

    def test_timefuncs_out_range2(self):
        start = CronTimer.to_cron("12:01am")
        end = CronTimer.to_cron("8:00am")
        now = CronTimer.to_cron("5:54pm")
        self.assertFalse(crontime_in_range(now, start, end))
    
    def test_timefuncs_in_range_flip(self):
        start = CronTimer.to_cron("10:03pm")
        end = CronTimer.to_cron("4:55am")
        now = CronTimer.to_cron("2:54am")
        self.assertTrue(crontime_in_range(now, start, end))
        
    def test_timefuncs_out_range_flip(self):
        start = CronTimer.to_cron("10:03pm")
        end = CronTimer.to_cron("4:55am")
        now = CronTimer.to_cron("2:54pm")
        self.assertFalse(crontime_in_range(now, start, end))
        


