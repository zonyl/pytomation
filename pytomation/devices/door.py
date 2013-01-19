from ..interfaces import Command
from .interface import InterfaceDevice
from .state import State

class Door(InterfaceDevice):
    STATES = [State.UNKNOWN, State.OPEN, State.CLOSED]
    COMMANDS = [Command.OPEN, Command.CLOSE, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]

    
    def _initial_vars(self, *args, **kwargs):
        super(Door, self)._initial_vars(*args, **kwargs)
        self._read_only = True
        self.mapped(command=Command.ON, mapped=Command.OPEN)
        self.mapped(command=Command.OFF, mapped=Command.CLOSE)