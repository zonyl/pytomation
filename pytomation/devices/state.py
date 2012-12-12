"""
State Device

Delegates:
    device.on_off(callback_for_off)

    callback_for_off is passed three args: state, previous_state, and source object
    
    * For any state callback use: device.on_any(callback_for_any_state)
"""
from datetime import datetime
from pytomation.utility import CronTimer
from pytomation.utility import PeriodicTimer
from pytomation.utility.timer import Timer as CTimer
from threading import Timer
from ..interfaces.common import Command
from ..common.pytomation_object import PytomationObject

class State(object):
    UNKNOWN = 'unknown'
    ON = Command.ON
    OFF = Command.OFF
    LIGHT = 'light'
    DARK = 'dark'
    MOTION = 'motion'
    STILL = 'still'
    PRESENCE = 'presence'
    VACANT = 'vacant'
    OPEN = 'open'
    CLOSED = 'closed'
    L10 = Command.L10
    L20 = Command.L20
    L30 = Command.L30
    L40 = Command.L40
    L50 = Command.L50
    L60 = Command.L60
    L70 = Command.L70
    L80 = Command.L80
    L90 = Command.L90
    
class StateDevice(PytomationObject):
    STATES = [State.ON, State.OFF, State.UNKNOWN]
    DELEGATE_PREFIX = 'on_'
    TIME_PREFIX = 'time_'
    DELAY_PREFIX = 'delay_'
    IGNORE_PREFIX = 'ignore_'
    IDLE_PREFIX = 'idle_'
    ANY_STATE = 'any'

    def __init__(self, devices=(), *args, **kwargs):
        super(StateDevice, self).__init__(*args, **kwargs)
#        devices = kwargs.get('devices', ())
        if not isinstance(devices, tuple):
            devices = (devices, )
        self._initial_vars()
        kwargs.update({'devices': devices})
        self._initial_state(*args, **kwargs)
        for k, v in kwargs.iteritems():
            try:
                getattr(self, k)(v)
            except Exception, ex:
                pass
        self._set_state(self._state, self._prev_state, self._prev_source)
    
    def _initial_state(self, *args, **kwargs):
        devices = kwargs.get('devices', ())
        prev_state = self._prev_state

        initial_state = kwargs.get('initial_state', None)
        if initial_state:
            try:
                
                self._state = self._state_map(initial_state.state, prev_state, initial_state)
                self._prev_source = initial_state
 #               self._set_state(initial_state.state, prev_state, initial_state)
            except AttributeError, ex:
                self._state = self._state_map(initial_state, prev_state, None)
#                self._set_state(initial_state, prev_state, None)
            self._prev_state = self._state
        else:
            self._state = State.UNKNOWN
            self._prev_state = self._state
            for device in devices:
                try:
                    m_state = self._state_map(device.state, prev_state, device)
                    self._state = m_state
#                    self._set_state(device.state, prev_state, device)
                    self._prev_state = self._state
                except:
                    pass
        self._logger.info('{name}-> Initial State: {state}'.format(name=self._name,
                                                                 state=self._state))

    def _initial_vars(self):
        self._state = State.UNKNOWN
        self._prev_state = State.UNKNOWN
        self._prev_source = None
        self._delegates = {}
        self._times = {}
        self._delays = {}
        self._ignores = []
        self._idle_timer = None
        self._last_set = datetime.now()
        pass

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        return self._state
    
    def devices(self, devices):
        if not isinstance(devices, tuple):
            devices = (devices, )
        self._bind_devices(devices)
        return devices
    
    @property
    def idle(self):
        difference = datetime.now() - self._last_set
        return difference.total_seconds()
    
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
        elif name[0:len(self.IDLE_PREFIX)] == self.IDLE_PREFIX:
            return lambda x: self._add_idle(name[len(self.IDLE_PREFIX):len(name)], x)
#        else:
#            return super(StateDevice, self).__getattr__(name)
#        raise AttributeError

    def _set_state(self, state, previous_state=None, source=None):
        source_name = None
        if source:
            source_name = source.name
            
        self._logger.debug('{device} Incoming Set state: {state} {previous_state} {source}'.format(
                             device=str(self),
                             state=state,
                             previous_state=previous_state,
                             source=source_name
                             ))
        if state in self._ignores:
            return None
        if not previous_state:
            previous_state = self._prev_state
            
        mapped_state = self._state_map(state, previous_state, source)
        if not mapped_state: # If we get no state, then ignore this state
            self._logger.info('{name}-> Ignored state "{state}" from source "{source}'.format(
                                                                                              name=self._name,
                                                                                              state=state,
                                                                                              source=source_name,
                                                                                              ))
            return False
        self._state = mapped_state
        self._logger.info('{name}-> received command "{state}" mapped to "{mapped}" from {source}, previously {previous_state}'.format(
                             name=self._name,
                             state=state,
                             mapped=mapped_state,
                             previous_state=previous_state,
                             source=source_name
                             ))
        self._delegate(mapped_state)

        self._trigger_delay(mapped_state, state, previous_state, source )

        self._trigger_idle(mapped_state, state, previous_state, source)

        self._prev_state = self._state
        self._last_set = datetime.now()
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
        delay = self._delays.get(state, None)
        if delay:
            del delay
        
        if secs:
#            self._delays.update({state: secs})
            timer = CTimer()
            timer.interval = secs
            self._delays.update({state: timer})

    def _trigger_delay(self, mapped_state, orig_state, prev_state, source):
        # start any delayed states
        if source != self:
            for d_state, timer in self._delays.iteritems():
                # only if we arent already that state
                if d_state != mapped_state:
                    timer.stop()
                    timer.action(self._set_state, (d_state, None, self))
#                    timer = Timer(secs, self._set_state, (d_state, self._prev_state, self))
#                    timer.setDaemon(True)
                    timer.start()
                elif d_state == orig_state:
                    timer.stop()
        return True

    def _add_idle(self, state, secs):
        if secs:
#            self._delays.update({state: secs})
            self._idle_timer = CTimer()
            self._idle_timer.interval = secs
            self._idle_timer.action(self._idle_action, (state, ))

    def _trigger_idle(self, mapped, state, previous_state, source):
        if mapped == State.ON and self._idle_timer and source != self:
            self._idle_timer.restart()

    def _idle_action(self, *args, **kwargs):
        state = args[0]
        return self._set_state(state, None, self)

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
#                self._logger.debug('{self}-> Delegate: {state} to {device}'.format(
#                                    self=self._name,
#                                     state=state,
#                                     device=str(delegate.name),
#                                                                                     ))
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
