from ..common import PytomationObject
from ..interfaces import Command
from ..utility import CronTimer

class State2(object):
    ALL = 'all'
    UNKNOWN = 'unknown'
    ON = 'on'
    OFF = 'off'
    LEVEL = 'level'
    
class State2Device(PytomationObject):
    STATES = [State2.UNKNOWN, State2.ON, State2.OFF, State2.LEVEL]
    COMMANDS = [Command.ON, Command.OFF, Command.LEVEL]
    
    def __init__(self, *args, **kwargs):
        super(State2Device, self).__init__(*args, **kwargs)
        self._initial_vars(*args, **kwargs)
        self._process_kwargs(kwargs)
        
    def _initial_vars(self, *args, **kwargs):
        self._state = State2.UNKNOWN
        self._delegates = []
        self._times = []
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        return self._state
    
    def __getattr__(self, name):
        # Give this object methods for each command supported
        if self._is_valid_command(name):
            return lambda *a, **k: self.command(name, *a, sub_state=a, **k)

    def command(self, command, *args, **kwargs):
        (state, map_command) = self._command_state_map(command, *args, **kwargs)
        if state and self._is_valid_state(state):
            self.state = state
            self._delegate_command(map_command)

    def _command_state_map(self, command, *args, **kwargs):
        if command == Command.ON:
            state = State2.ON
            m_command = Command.ON
        elif command == Command.OFF:
            state = State2.OFF
            m_command = Command.OFF
        elif command == Command.LEVEL:
            state = (State2.LEVEL, kwargs.get('sub_state', (0,))[0])
            m_command = Command.LEVEL
        return (state, m_command)

    def _process_kwargs(self, kwargs):
        # Process each initializing attribute as a method call on this object
        for k, v in kwargs.iteritems():
            try:
                getattr(self, k)(**v)
            except:
                getattr(self, k)(v)
            
    def _is_valid_state(self, state):
        isFound = state in self.STATES
        if not isFound:
            try:
                isFound = state[0] in self.STATES
            except:
                pass
        return isFound

    def _is_valid_command(self, command):
        return command in self.COMMANDS

    def initial(self, state):
        self.state = state
        
    def time(self, *args, **kwargs):
        # time, command
        times = kwargs.get('time', None)
        command = kwargs.get('command', State2.UNKNOWN)
        
        if times:
            if not isinstance( times, tuple):
                times = (times, )
            for time in times:
                timer = CronTimer()
                if isinstance(time, tuple):
                    timer.interval(*time)
                else:
                    timer.interval(*CronTimer.to_cron(time))
                timer.action(self.command, (command))
                timer.start()
                self._times.append((command, timer))

    def on_command(self, device=None):
        self._delegates.append(device)
    
    def _delegate_command(self, command):
        for delegate in self._delegates:
            delegate.command(command=command, source=self)
        
    def devices(self, *args, **kwargs):
        devices = args[0]

        if not isinstance(devices, tuple):
            devices = (devices, )
                   
        for device in devices:
            if device:
                device.on_command(device=self)

            