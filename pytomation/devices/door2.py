from ..interfaces import Command
from .interface2 import Interface2Device
from .state2 import State2

class Door2(Interface2Device):
    STATES = [State2.UNKNOWN, State2.OPEN, State2.CLOSED]
    COMMANDS = [Command.ON, Command.OFF, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]

    
    def _initial_vars(self, *args, **kwargs):
        super(Door2, self)._initial_vars(*args, **kwargs)
        self._read_only = True
        
    def _command_state_map(self, command, *args, **kwargs):
        (m_state, m_command) = super(Door2, self)._command_state_map(command, *args, **kwargs)
        if m_command == Command.OFF:
            m_state = State2.CLOSED
        elif m_command == Command.ON:
            m_state = State2.OPEN
        return (m_state, m_command)