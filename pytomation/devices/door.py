from ..interfaces import Command
from .interface import Interface2Device
from .state import State2

class Door2(Interface2Device):
    STATES = [State2.UNKNOWN, State2.OPEN, State2.CLOSED]
    COMMANDS = [Command.OPEN, Command.CLOSE, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]

    
    def _initial_vars(self, *args, **kwargs):
        super(Door2, self)._initial_vars(*args, **kwargs)
        self._read_only = True
        self.mapped(command=Command.ON, mapped=Command.OPEN)
        self.mapped(command=Command.OFF, mapped=Command.CLOSE)