# CronTimer
# Based on code from:
#  Brian @  http://stackoverflow.com/questions/373335/suggestions-for-a-cron-like-scheduler-in-python

# references:
# http://docs.python.org/library/sched.html

import time
from datetime import datetime, timedelta
from threading import Timer


# Some utility classes / functions first
class AllMatch(set):
    """Universal set - match everything"""
    def __contains__(self, item): return True

allMatch = AllMatch()

def conv_to_set(obj):  # Allow single integer to be provided
    if isinstance(obj, (int,long)):
        return set([obj])  # Single item
    if not isinstance(obj, set):
        obj = set(obj)
    return obj

# The actual Event class
class CronTimer(object):
    FREQUENCY = 1

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.running = False
        self.timer = Timer(self.FREQUENCY, self._check_for_event, ())

    def interval(self, secs=allMatch, min=allMatch, hour=allMatch, 
                       day=allMatch, month=allMatch, dow=allMatch ):
        self.secs = conv_to_set(secs)
        self.mins = conv_to_set(min)
        self.hours = conv_to_set(hour)
        self.days = conv_to_set(day)
        self.months = conv_to_set(month)
        self.dow = conv_to_set(dow)

    def action(self, action, action_args):
        self.action = action
        self.action_args = action_args

    def run(self):
        self.running = True
        self.timer.run()

    def matchtime(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.second     in self.secs) and
                (t.minute     in self.mins) and
                (t.hour       in self.hours) and
                (t.day        in self.days) and
                (t.month      in self.months) and
                (t.weekday()  in self.dow))

    def _check_for_event(self):
        if self.running:
            t = datetime(*datetime.now().timetuple()[:6])
            if self.matchtime(t):
                self.action(*self.args, **self.kwargs)