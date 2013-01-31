import time
from datetime import datetime, timedelta
from threading import Timer as PTimer, Event


# The actual Event class
class Timer(object):

    def __init__(self, secs=60, *args, **kwargs):
        self._timer = None
        self._secs = secs
        
    def _get_timer(self, secs):
        timer = PTimer(secs, self._run_action, ())
        timer.daemon = True
        return timer

    @property
    def interval(self):
        return self._secs

    @interval.setter
    def interval(self, secs):
        self.stop()
        self._secs = secs
        return secs

    def action(self, action, action_args, **kwargs):
        self._action = action
        self._action_args = action_args
        self._action_kwargs = kwargs
    
    def _run_action(self):
        if self._action:
            if isinstance(self._action_args, tuple):
                self._action(*self._action_args, **self._action_kwargs)
            else:
                self._action(self._action_args, **self._action_kwargs)
        else:
            self.stop()

    def start(self):
        self.stop()
        self._timer = self._get_timer(self._secs)
        self._timer.start()
            
    def stop(self):
        if self._timer and self._timer.isAlive():
            self._timer.cancel()
        if self._timer:
            del(self._timer)
        self._timer = None
        
    def restart(self):
        self.stop()
        self.start()

