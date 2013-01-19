import ephem
import pytz

from datetime import datetime
from time import strftime
from .state import State2Device, State2
from pytomation.utility import CronTimer
from ..interfaces import Command

class Location2(State2Device):
    STATES = [State2.LIGHT, State2.DARK]
    COMMANDS = [Command.LIGHT, Command.DARK, Command.INITIAL, Command.TOGGLE, Command.PREVIOUS]

    class MODE():
        STANDARD = '0'
        CIVIL = '-6'
        NAUTICAL = '-12'
        ASTRONOMICAL = '-18'
    
    def __init__(self, latitude, longitude, tz='US/Eastern', mode=MODE.STANDARD, is_dst=True, *args, **kwargs):
        super(Location2, self).__init__(*args, **kwargs)
        self.obs = ephem.Observer()
        self.obs.lat = latitude
        self.obs.long = longitude
        self.tz = pytz.timezone(tz)
        self.is_dst = is_dst

        self.sun = ephem.Sun(self.obs)
        self._horizon = mode
        
        self._sunset_timer = CronTimer()
        self._sunrise_timer = CronTimer()
        self._local_time = None
        self._recalc()

    @property
    def mode(self):
        return self._horizon
    
    @mode.setter
    def mode(self, value):
        self._horizon = value
        self._recalc()
        
        
    @property
    def local_time(self):
        if not self._local_time:
            return self.tz.localize(datetime.now(), is_dst=self.is_dst)
        else:
            return self.tz.localize(self._local_time, is_dst=self.is_dst)
    
    @local_time.setter
    def local_time(self, value):
        self._local_time = value
        self._recalc()

    def _recalc(self):
        self.obs.horizon = self._horizon

#        midnight = self.tz.localize(local_time.replace(hour=12, minute=0, second=0, microsecond=0, tzinfo=None), 
#                               is_dst=None)
#        self.obs.date = midnight.astimezone(pytz.utc) 

        self.obs.date = self.local_time.astimezone(pytz.utc)

        prev_rising = self._utc2tz(
                                  self.obs.previous_rising(self.sun, use_center=True).datetime())
        prev_setting = self._utc2tz(
                                  self.obs.previous_setting(self.sun, use_center=True).datetime())
        self._sunrise = self._utc2tz(
                                     self.obs.next_rising(self.sun, use_center=True).datetime())
        self._sunset = self._utc2tz(
                                     self.obs.next_setting(self.sun, use_center=True).datetime())
        self._sunrise = self._sunrise.replace(second=0, microsecond=0)
        self._sunset = self._sunset.replace(second=0, microsecond=0)
        self._logger.info('{name} Location sunset: {sunset} sunrise: {sunrise}'.format(
                                                                                       name=self.name,
                                                                                       sunset=str(self._sunset),
                                                                                       sunrise=str(self._sunrise),
                                                                                       ))
        time_now = self.local_time.replace(second=0, microsecond=0)
        if (self._sunrise > self._sunset and self._sunset != time_now) or \
            self._sunrise == time_now:
#            self.state = State2.LIGHT
#            self._set_state(State.LIGHT, self.state, self)
            if self.state <> Command.LIGHT:
#                self.command(Command.LIGHT, source=self)
                self.light()
        else:
#            self.state = State2.DARK
#            self._set_state(State.DARK, self.state, self)
            if self.state <> Command.DARK:
#                self.command(Command.DARK, source=self)
                self.dark()           
        # Setup trigger for next transition
        sunset_t = self._sunset_timer
#        sunset_t.stop()
        sunset_t.interval(*CronTimer.to_cron(strftime("%H:%M:%S", self.sunset.timetuple())))
        sunset_t.action(self._recalc)
        sunset_t.start()

#        self._sunrise_timer.stop()
        self._sunrise_timer.interval(*CronTimer.to_cron(strftime("%H:%M:%S", self.sunrise.timetuple())))
        self._sunrise_timer.action(self._recalc, ())
        self._sunrise_timer.start()    
        

    @property
    def sunset(self):
        return self._sunset
    
    @sunset.setter
    def sunset(self, value):
        self._sunset = value
        self._recalc()
        return self._sunset
    
    @property
    def sunrise(self):
        return self._sunrise
    
    @sunrise.setter
    def sunrise(self, value):
        self._sunrise = value
        self._recalc()
        return self._sunrise

    def _utc2tz(self, value):
        return pytz.utc.localize(value, is_dst=self.is_dst).astimezone(self.tz)

    def _command_state_map(self, command, *args, **kwargs):
        (m_state, m_command) = super(Location2, self)._command_state_map(command, *args, **kwargs)
        if m_command == Command.OFF:
            m_state = State2.DARK
        elif m_command == Command.ON:
            m_state = State2.LIGHT
        return (m_state, m_command)