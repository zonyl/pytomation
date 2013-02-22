# CronTimer
# Based on code from:
#  Brian @  http://stackoverflow.com/questions/373335/suggestions-for-a-cron-like-scheduler-in-python

# references:
# http://docs.python.org/library/sched.html

import time
from datetime import datetime, timedelta
from threading import Timer, Event

from .periodic_timer import PeriodicTimer

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

        self.timer = PeriodicTimer(self.FREQUENCY)
        self.timer.action(self._check_for_event)

    def interval(self, secs=allMatch, min=allMatch, hour=allMatch,
                       day=allMatch, month=allMatch, dow=allMatch):
        if secs=='*':
            secs=allMatch
        if min=='*':
            min=allMatch
        if hour=='*':
            hour=allMatch
        if day=='*':
            day=allMatch
        if month=='*':
            month=allMatch
        if dow=='*':
            dow=allMatch
        self.secs = conv_to_set(secs)
        self.mins = conv_to_set(min)
        self.hours = conv_to_set(hour)
        self.days = conv_to_set(day)
        self.months = conv_to_set(month)
        self.dow = conv_to_set(dow)

    def action(self, action, action_args=()):
        self._action = action
        self._action_args = action_args

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def matchtime(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.second     in self.secs) and
                (t.minute     in self.mins) and
                (t.hour       in self.hours) and
                (t.day        in self.days) and
                (t.month      in self.months) and
                (t.isoweekday()  in self.dow))

    def _check_for_event(self, *args, **kwargs):
        if datetime:
            t = datetime(*datetime.now().timetuple()[:6])
    #        print 'Time: ' + str(t) + ":" + str(self.secs)
            if self.matchtime(t):
    #            print 'Run action'
                if len(self._action_args) > 0:
                    self._action(self._action_args)
                else:
                    self._action()
                
    @staticmethod
    def to_cron(string):
        date_object = None
        try: # Hours / Minutes
            try:
                date_object = datetime.strptime(string, '%I:%M%p')
            except:
                try:
                    date_object = datetime.strptime(string, '%I:%M %p')
                except:
                        date_object = datetime.strptime(string, '%H:%M')
            return (
                    0,
                    date_object.minute,
                    date_object.hour,
                    allMatch,
                    allMatch,
                    allMatch,
                    )
#            td = timedelta(
#                           years=0,
#                           months=0,
#                           days=0,
#                           hours=date_object.hour, 
#                           minutes=date_object.minute,
#                           seconds=0)
        except Exception, e:
            try: # Hours / Minutes / Seconds
                try:
                    date_object = datetime.strptime(string, '%I:%M:%S%p')
                except:
                    try:
                        date_object = datetime.strptime(string, '%I:%M:%S %p')
                    except:
                        date_object = datetime.strptime(string, '%H:%M:%S')
                return (
                    date_object.second,
                    date_object.minute,
                    date_object.hour,
                    allMatch,
                    allMatch,
                    allMatch,
                    )
            except:
                pass
#        date_object = datetime.strptime(string, '%b %d %Y %I:%M%p')
        return None
