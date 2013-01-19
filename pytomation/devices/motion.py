from ..interfaces import Command
from .interface import Interface2Device
from .state import State

class Motion2(Interface2Device):
    STATES = [State.UNKNOWN, State.MOTION, State.STILL, State.LEVEL]
    COMMANDS = [Command.MOTION, Command.STILL, Command.LEVEL, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]

    def _initial_vars(self, *args, **kwargs):
        super(Motion2, self)._initial_vars(*args, **kwargs)
        self._read_only = True
        self.mapped(command=Command.ON, mapped=Command.MOTION)
        self.mapped(command=Command.OFF, mapped=Command.STILL)
                
#    def _command_state_map(self, command, *args, **kwargs):
#        (m_state, m_command) = super(Motion2, self)._command_state_map(command, *args, **kwargs)
#        if m_command == Command.OFF:
#            m_state = State.STILL
#            m_command = Command.STILL
#        elif m_command == Command.ON:
#            m_state = State.MOTION
#            m_command = Command.MOTION
#        return (m_state, m_command)