from ..common import PytomationObject
from ..interfaces import Command

class State2(object):
    ON = 'on'
    OFF = 'off'
    UNKNOWN = 'unknown'
    
    
class State2Device(PytomationObject):
    STATES = [State2.UNKNOWN, State2.ON, State2.OFF]
    
    def __init__(self, *args, **kwargs):
        super(State2Device, self).__init__(*args, **kwargs)
        self._state = State2.UNKNOWN
        self._process_kwargs(kwargs)
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        return self._state
    
    def __getattr__(self, name):
        if name in (Command.ON, Command.OFF):
            return lambda *a, **k: self.command(name, *a, **k)

    def command(self, command):
        if command == Command.ON:
            self.state = State2.ON
        elif command == Command.OFF:
            self.state = State2.OFF
        
    
    def _process_kwargs(self, kwargs):
        for k, v in kwargs.iteritems():
            getattr(self, k)(v)
        
    def initial(self, state):
        self.state = state