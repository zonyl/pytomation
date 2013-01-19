from .interface import Interface2Device
from .state import State
from ..interfaces import Command

class Photocell2(Interface2Device):
    STATES = [State.UNKNOWN, State.DARK, State.LIGHT, State.LEVEL]
    COMMANDS = [Command.DARK, Command.LIGHT, Command.LEVEL, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]

    def _initial_vars(self, *args, **kwargs):
        super(Photocell2, self)._initial_vars(*args, **kwargs)
        self._read_only = True
        self.mapped(command=Command.ON, mapped=Command.DARK)
        self.mapped(command=Command.OFF, mapped=Command.LIGHT)