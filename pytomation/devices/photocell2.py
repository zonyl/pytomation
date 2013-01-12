from .interface2 import Interface2Device
from .state2 import State2
from ..interfaces import Command

class Photocell2(Interface2Device):
    STATES = [State2.UNKNOWN, State2.DARK, State2.LIGHT, State2.LEVEL]
    COMMANDS = [Command.DARK, Command.LIGHT, Command.LEVEL, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]

    def _initial_vars(self, *args, **kwargs):
        super(Photocell2, self)._initial_vars(*args, **kwargs)
        self._read_only = True
        self.mapped(command=Command.ON, mapped=Command.DARK)
        self.mapped(command=Command.OFF, mapped=Command.LIGHT)