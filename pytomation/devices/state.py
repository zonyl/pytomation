"""
State Device

Delegates:
    device.on_off(callback_for_off)

    callback_for_off is passed three args: state, previous_state, and source object
    
    * For any state callback use: device.on_any(callback_for_any_state)
"""
from pytomation.utility import CronTimer
from threading import Timer
from ..interfaces.common import *

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
    DELAY_PREFIX = 'delay_'
    IGNORE_PREFIX = 'ignore_'
    ANY_STATE = 'any'


    def __init__(self, devices=(), initial_state=None):
        if not isinstance(devices, tuple):
            devices = (devices, )
        self._initial_vars()
        self._initial_state(devices, initial_state)
        self._bind_devices(devices)

    def _initial_state(self, devices, initial_state):
        if initial_state:
            self._state = initial_state
            self._prev_state = initial_state
        else:
            self._state = State.UNKNOWN
            self._prev_state = self._state
            for device in devices:
                try:
                    m_state = self._state_map(device.state, self._prev_state, device)
                    self._state = m_state
                    self._prev_state = self._state
                except:
                    pass

    def _initial_vars(self):
        self._state = State.UNKNOWN
        self._prev_state = State.UNKNOWN
        self._delegates = {}
        self._times = {}
        self._delays = {}
        self._ignores = []
        pass

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
        elif name[0:len(self.DELAY_PREFIX)] == self.DELAY_PREFIX:
            return lambda x: self._add_delay(name[len(self.DELAY_PREFIX):len(name)], x)
        elif name[0:len(self.IGNORE_PREFIX)] == self.IGNORE_PREFIX:
            return lambda x=True: self._add_ignore(name[len(self.IGNORE_PREFIX):len(name)], x)
#        else:
#            return super(StateDevice, self).__getattr__(name)
        raise AttributeError

    def _set_state(self, state, previous_state=None, source=None):
        pylog(__name__,'{device} Incoming Set state: {state} {previous_state} {source}'.format(
                             device=self,
                             state=state,
                             previous_state=previous_state,
                             source=source
                                                                             ))
        if state in self._ignores:
            return None
        state = self._state_map(state, previous_state, source)
        if not state: # If we get no state, then ignore this state
            return False
        self._state = state
        pylog(__name__,'{device} Mapped Set state: {state} {previous_state} {source}'.format(
                             device=self,
                             state=state,
                             previous_state=previous_state,
                             source=source
                             ))
        self._delegate(state)

        # start any delayed states
        if source != self:
            for d_state, secs in self._delays.iteritems():
                # only if we arent already that state
                if d_state != state:
                    timer = Timer(secs, self._set_state, (d_state, self._prev_state, self))
                    timer.setDaemon(True)
                    timer.start()

        self._prev_state = self._state
        return True

    def _state_map(self, state, previous_state=None, source=None):
        return state
    
    def _add_delegate(self, state, callback):
        try:
            a = self._delegates
        except AttributeError, ex:
            self._delegates = {}
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
    
    def _add_delay(self, state, secs):
        timer = self._delays.get(state, None)
        if timer:
            del timer
        
        if secs:
            self._delays.update({state: secs})
        
    def _add_ignore(self, state, value=True):
        if value:
            self._ignores.append(state)
        else:
            self._ignores = [x for x in self._ignores if x != state]

    def _delegate(self, state):
        delegate_list = self._delegates.get(state, [])
        any_delegate_list = self._delegates.get(self.ANY_STATE, [])
        delegate_list += any_delegate_list
        if delegate_list:
            for delegate in delegate_list:
                pylog(__name__,'{device} Delegate: {state}'.format(
                                    device=self,
                                     state=state,
                                                                                     ))
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
