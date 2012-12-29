from datetime import datetime

from ..common import PytomationObject
from ..interfaces import Command
from ..utility import CronTimer
from ..utility.timer import Timer as CTimer

class State2(object):
    ALL = 'all'
    UNKNOWN = 'unknown'
    ON = 'on'
    OFF = 'off'
    LEVEL = 'level'
    MOTION = 'motion'
    STILL = 'still'
    OPEN = 'open'
    CLOSED = "closed"
    LIGHT = "light"
    DARK = "dark"
    
class State2Device(PytomationObject):
    STATES = [State2.UNKNOWN, State2.ON, State2.OFF, State2.LEVEL]
    COMMANDS = [Command.ON, Command.OFF, Command.LEVEL, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]
    
    def __init__(self, *args, **kwargs):
        super(State2Device, self).__init__(*args, **kwargs)
        if not kwargs.get('devices', None) and len(args)>0:
            kwargs.update({'devices': args[0]})
        self._initial_vars(*args, **kwargs)
        self._process_kwargs(kwargs)
        self.command(Command.INITIAL, source=self)
        
    def _initial_vars(self, *args, **kwargs):
        self._state = State2.UNKNOWN
        self._last_set = datetime.now()
        self._delegates = []
        self._times = []
        self._maps = []
        self._delays = []
        self._ignores = []
        self._idle_timer = None
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._previous_state = self._state
        self._last_set = datetime.now()
        self._state = value
        if self._idle_timer:
            self._idle_timer.start()
        return self._state
    
    def __getattr__(self, name):
        # Give this object methods for each command supported
        if self._is_valid_command(name):
            return lambda *a, **k: self.command(name, *a, sub_state=a, **k)

    def command(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        if not self._is_ignored(command, source):
            m_command = self._process_maps(*args, command=command, **kwargs)
            if m_command != command:
                self._logger.debug("{name} Map from '{command}' to '{m_command}'".format(
                                                                        name=self.name,
                                                                        command=command,
                                                                        m_command=m_command,
                                                                                         ))
            (state, map_command) = self._command_state_map(m_command, *args, **kwargs)
    
            if state and map_command and self._is_valid_state(state):
                if source == self or not self._is_delayed(map_command):
                    self._logger.info('{name} changed state to state "{state}" by command {command} from {source}'.format(
                                                      name=self.name,
                                                      state=state,
                                                      command=map_command,
                                                      source=source.name if source else None,
                                                                                                                  ))
                    self.state = state
                    self._delegate_command(map_command)
                else:
                    self._delay_start(map_command, source)
            else:
                self._logger.debug("{name} ignored command {command} from {source}".format(
                                                                                           name=self.name,
                                                                                           command=command,
                                                                                           source=source.name
                                                                                           ))

    def _command_state_map(self, command, *args, **kwargs):
        state = None
        m_command = command
        if command == Command.ON:
            state = State2.ON
            m_command = Command.ON
        elif command == Command.OFF:
            state = State2.OFF
            m_command = Command.OFF
        elif command == Command.LEVEL or (isinstance(command, tuple) and command[0] == Command.LEVEL):
            if isinstance(command, tuple):
                state = (State2.LEVEL, command[1])
                m_command = command
            else:
                state = (State2.LEVEL, kwargs.get('sub_state', (0,))[0])
                m_command = (Command.LEVEL,  kwargs.get('sub_state', (0,) ))
        elif command == Command.PREVIOUS:
            state = self._previous_state
            m_command = command
        elif command == Command.TOGGLE:
            if self.state == State2.ON:
                state = State2.OFF
            else:
                state = State2.ON
            m_command = command
        elif command == Command.INITIAL:
            state = self.state

        return (state, m_command)

    def _process_kwargs(self, kwargs):
        # Process each initializing attribute as a method call on this object
        for k, v in kwargs.iteritems():
            try:
                getattr(self, k)(**v)
            except Exception, ex:
                getattr(self, k)(v)
            
    def _process_maps(self, *args, **kwargs):
        source = kwargs.get('source', None)
        command = kwargs.get('command', None)
        for mapped in self._maps:
            if mapped['command'] == command and \
                (mapped['source'] == source or not mapped['source']):
                command = mapped['mapped']
        return command
 
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
        try: # Check to see if this is a device reference
            self.state = state.state
        except: # Just a value
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
                self._add_device(device)

    def _add_device(self, device):
        return device.on_command(device=self)

    def mapped(self, *args, **kwargs):
        command = kwargs.get('command', None)
        mapped = kwargs.get('mapped', None)
        source = kwargs.get('source', None)
        self._maps.append({'command': command, 'mapped': mapped, 'source': source})
        
    def delay(self, *args, **kwargs):
        command = kwargs.get('command', None)
        mapped = kwargs.get('mapped', None)
        if not mapped:
            mapped = command
        source = kwargs.get('source', None)
        secs = kwargs.get('secs', None)
        timer = CTimer()
        timer.interval=secs
        timer.action(self.command, (mapped, ), source=self)
#            timer.action(self.command, (mapped), source=self)
        self._delays.append({'command': command, 'mapped': mapped, 'source': source, 'secs': secs, 'timer': timer})

    def _is_delayed(self, command):
        return command in [ delay['command'] for delay in self._delays]
    
    def _delay_start(self, command, source):
        for delay in self._delays:
            if delay['command'] == command and (delay['source'] == None or delay['source'] == source):
                delay['timer'].start()
                
    @property
    def idle_time(self):
        difference = datetime.now() - self._last_set
        return difference.total_seconds()

    def idle(self, *args, **kwargs):
        command = kwargs.get('command', None)
        secs = kwargs.get('secs', None)
        if secs:
            timer = CTimer()
            timer.interval = secs
            timer.action(self.command, (command, ), source=self)
            self._idle_timer = timer
            
    def ignore(self, *args, **kwargs):
        command = kwargs.get('command', None)
        source = kwargs.get('source', None)
        self._ignores.append({'command': command,'source': source})
        
    def _is_ignored(self, command, source):
        for ignore in self._ignores:
            if ignore['command'] == command and \
            (ignore['source'] == None or ignore['source'] == source):
                return True
        return False