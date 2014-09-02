import time
from datetime import datetime, timedelta
from threading import Event
from apscheduler.schedulers.background import BackgroundScheduler


# The actual Event class
class PeriodicTimer(object):
    sched = None
    
    def __init__(self, frequency=60, *args, **kwargs):
        # Start the scheduler
        self.frequency = frequency

        self.scheduler_start()
        
        self._job = None
        self.is_stopped = Event()
        self.is_stopped.clear()

#         self.interval = frequency
#         self._timer = Timer(self.frequency, self._check_for_event, ())
        self.interval = frequency    

    def scheduler_start(self):
        if not PeriodicTimer.sched:
            PeriodicTimer.sched = BackgroundScheduler()
        if not PeriodicTimer.sched.running:
            PeriodicTimer.sched.start()

    @property
    def interval(self):
        return self.frequency

    @interval.setter
    def interval(self, frequency):
        self.frequency = frequency
        self.start()
        return self.frequency

    def action(self, action, *action_args, **kwargs):
        self._action = action
        self._action_args = action_args
        self._action_kwargs = kwargs

    def start(self):
#        if self._sched.running:
#            self._sched.shutdown()
        if not PeriodicTimer.sched:
            return

        self.stop()

        self._job = PeriodicTimer.sched.add_job(self._check_for_event, trigger="interval", seconds = self.frequency, max_instances=10, misfire_grace_time=10, coalesce=False)
        self.is_stopped.clear()

    def stop(self):
        if self._job:
            PeriodicTimer.sched.remove_job(self._job.id)
        self.is_stopped.set()        

    def _check_for_event(self):
        if self.is_stopped.isSet():
            return
        if self._action:
            self._action(*self._action_args, **self._action_kwargs)
        else:
            self.stop()