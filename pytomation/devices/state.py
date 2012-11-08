"""
State Device

Delegates:
    device.on_off(callback_for_off)

    callback_for_off is passed three args: state, previous_state, and source object
    
    * For any state callback use: device.on_any(callback_for_any_state)
"""
from pytomation.utility import CronTimer


class State(object):
    UNKNOWN = 'unknown'
    ON = 'on'
    OFF = 'off'
    LIGHT = 'light'
    DARK = 'dark'
    MOTION = 'motion'
    STILL = 'still'
    PRESENCE = 'presence'
    VACANT = 'vacant'
    OPEN = 'open'
    CLOSED = 'closed'

class StateDevice(object):
    STATES = [State.ON, State.OFF, State.UNKNOWN]
    DELEGATE_PREFIX = 'on_'
    TIME_PREFIX = 'time_'
    ANY_STATE = 'any'


    def __init__(self, *devices):
        self._state = State.UNKNOWN
        self._prev_state = State.UNKNOWN
        self._delegates = {}
        self._times = {}
        self._bind_devices(devices)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        return self._state
    
    def __getattr__(self, name):
        #state functions
        if name.lower() in [ n.lower() for n in self.STATES]:
            if name == name.upper():
                return name.lower()
            else:
                return lambda x=None, y=None: self._set_state(name, x, y)
        elif name[0:len(self.DELEGATE_PREFIX)] == self.DELEGATE_PREFIX:
            return lambda x: self._add_delegate(name[len(self.DELEGATE_PREFIX):len(name)], x)
        elif name[0:len(self.TIME_PREFIX)] == self.TIME_PREFIX:
            return lambda x: self._add_time(name[len(self.TIME_PREFIX):len(name)], x)
#        else:
#            return super(StateDevice, self).__getattr__(self)
#        raise AttributeError

#    def __setattr__(self, name, value):
#        if name in self.STATES:
#            self._state = name
#        else:
#            return super(StateDevice, self).__setattr__(name, value)

    def _set_state(self, state, previous_state=None, source=None):
        self._state = state
        self._delegate(state)
        self._prev_state = self._state
        return True

    def _add_delegate(self, state, callback):
        state_list = self._delegates.get(state, None)
        if state_list:
            state_list.append(callback)
        else:
            self._delegates[state] = [callback]
        return True
    
    def _add_time(self, state, time):
        
        timer = self._times.get(state, None)
        if timer:
            del timer
        
        if time:
            timer = CronTimer()
            if isinstance(time, tuple):
                timer.interval(*time)
            else:
                timer.interval(*CronTimer.to_cron(time))
            timer.action(self._set_state, (state))
            timer.start()
            self._times.update({state: timer})
    
    def _delegate(self, state):
        delegate_list = self._delegates.get(state, [])
        any_delegate_list = self._delegates.get(self.ANY_STATE, [])
        delegate_list += any_delegate_list
        if delegate_list:
            for delegate in delegate_list:
                delegate(state=state, previous_state=self._prev_state, source=self)

    def _bind_devices(self, devices):
        for device in devices:
            try:
                device._add_delegate(self.ANY_STATE, self._set_state)
            except Exception, ex:
                pass
#            for state in self.STATES:
#                try:
##                    device._set_state(state)
##                    getattr(device, self.DELEGATE_PREFIX + state )(getattr(self, state))
#                    device._add_delegate(state, self._set_state)
#                except Exception, ex:
#                    pass
        return True
