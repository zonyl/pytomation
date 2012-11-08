import time
from datetime import datetime, timedelta
from threading import Timer, Event


# The actual Event class
class PeriodicTimer(object):

    def __init__(self, frequency=60, *args, **kwargs):
        self.is_stopped = Event()
        self.is_stopped.clear()

        self.interval = frequency
        self.timer = Timer(self.frequency, self._check_for_event, ())
        self.timer.daemon = True

    @property
    def interval(self):
        return self.frequency

    @interval.setter
    def interval(self, frequency):
        self.frequency = frequency
        self.stop()
        self.timer = Timer(self.frequency, self._check_for_event, ())
        return self.frequency

    def action(self, action, *action_args, **kwargs):
        self._action = action
        self._action_args = action_args
        self._action_kwargs = kwargs

    def start(self):
        self.is_stopped.clear()
        if not self.timer.isAlive():
            self.timer.start()

    def stop(self):
        self.is_stopped.set()

    def _check_for_event(self):
        while not self.is_stopped.isSet():
            if self.is_stopped.isSet():
                break
            if self._action:
                self._action(*self._action_args, **self._action_kwargs)
            else:
                self.stop()
            # Handle not so graceful shutdown
            try:
                self.is_stopped.wait(self.frequency)
            except:
                pass