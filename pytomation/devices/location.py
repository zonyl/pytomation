import ephem

from datetime import datetime
from time import strftime
from .state import StateDevice, State
from pytomation.utility import CronTimer

class Location(StateDevice):
    STATES = [State.LIGHT, State.DARK]

    class MODE():
        STANDARD = 0
        CIVIL = -6
        NAUTICAL = -12
        ASTRONOMICAL = -18
        
    _mode = MODE.STANDARD
    
    def __init__(self, latitude, longitude, tz=-5, mode=MODE.STANDARD):
        self.obs = ephem.Observer()
        self.obs.lat = latitude
        self.obs.long = longitude
        self.tz = tz
        
        self.sun = ephem.Sun(self.obs)
        if mode:
            self._horizon = mode
        
        self._sunset_timer = CronTimer()
        self._sunrise_timer = CronTimer()
        self._evaluate()

    @property
    def mode(self):
        return self._horizon
    
    @mode.setter
    def mode(self, value):
        self._horizon = value
        self._evaluate()

    def _evaluate(self):
        self.obs.horizon = self._horizon
        self.obs.date = datetime.now()
        # What is it now?
        prev_rising = self.obs.previous_rising(self.sun, use_center=True)
        prev_setting = self.obs.previous_setting(self.sun, use_center=True)
        if prev_rising > prev_setting:
            self.state = State.LIGHT
        else:
            self.state = State.DARK
        # Setup trigger for next transition
        next_rising = self.obs.next_rising(self.sun, use_center=True)
        next_setting = self.obs.next_setting(self.sun, use_center=True)
        
        self._sunset_time.stop()
        self._sunset_timer.interval(CronTimer.to_cron(strftime("%H:%M:%S", next_setting)))
        self._sunset_timer.action(self._evaluate)
        self._sunset_timer.start()

        self._sunrise_timer.stop()
        self._sunrise_timer.interval(CronTimer.to_cron(strftime("%H:%M:%S", next_rising)))
        self._sunrise_timer.action(self._evaluate)
        self._sunrise_timer.start()

#        self.obs.previous_rising(self.sun, use_center=True)
#        self.obs.next_setting(self.sun, use_center=True)
        
        