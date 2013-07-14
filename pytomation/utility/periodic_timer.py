import time
from datetime import datetime, timedelta
from threading import Event
from apscheduler.scheduler import Scheduler


# The actual Event class
class PeriodicTimer(object):
        
    def __init__(self, frequency=60, *args, **kwargs):
        # Start the scheduler
        self.frequency = frequency
        self._sched = Scheduler()
        self.is_stopped = Event()
        self.is_stopped.clear()

#         self.interval = frequency
#         self._timer = Timer(self.frequency, self._check_for_event, ())
        self.interval = frequency    

    @property
    def interval(self):
        return self.frequency

    @interval.setter
    def interval(self, frequency):
        self.frequency = frequency
        self.stop()
        self.dispose()
        self._sched = Scheduler()
        self._sched.add_interval_job(self._check_for_event, seconds = frequency)
        return self.frequency

    def action(self, action, *action_args, **kwargs):
        self._action = action
        self._action_args = action_args
        self._action_kwargs = kwargs

    def start(self):
        self.is_stopped.clear()
        self._sched.start()

    def stop(self):
        self.is_stopped.set()
        self._sched.shutdown()
        
    def dispose(self):
        try:
            if self._sched:
                self._sched.shutdown()
                del(self._sched)
        except:
            pass
        

    def _check_for_event(self):
        if self.is_stopped.isSet():
            return
        if self._action:
            self._action(*self._action_args, **self._action_kwargs)
        else:
            self.stop()