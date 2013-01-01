from .interface2 import Interface2Device
from .state2 import State2
from ..interfaces import Command

class Photocell2(Interface2Device):
    STATES = [State2.UNKNOWN, State2.DARK, State2.LIGHT, State2.LEVEL]
    COMMANDS = [Command.DARK, Command.LIGHT, Command.LEVEL, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]

    def _initial_vars(self, *args, **kwargs):
        super(Photocell2, self)._initial_vars(*args, **kwargs)
        self._read_only = True
       
    def _command_state_map(self, command, *args, **kwargs):
        (m_state, m_command) = super(Photocell2, self)._command_state_map(command, *args, **kwargs)
        if m_command == Command.OFF:
            m_state = State2.LIGHT
        elif m_command == Command.ON:
            m_state = State2.DARK
        return (m_state, m_command)