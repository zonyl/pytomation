from ..interfaces import Command
from .interface import InterfaceDevice
from .state import State

class Motion(InterfaceDevice):
    STATES = [State.UNKNOWN, State.MOTION, State.STILL, State.LEVEL]
    COMMANDS = [Command.MOTION, Command.STILL, Command.LEVEL,
                Command.PREVIOUS, Command.TOGGLE, Command.INITIAL,
                Command.AUTOMATIC, Command.MANUAL, Command.STATUS]

    def _initial_vars(self, *args, **kwargs):
        super(Motion, self)._initial_vars(*args, **kwargs)
        self._read_only = True
        self.mapped(command=Command.ON, mapped=Command.MOTION)
        self.mapped(command=Command.OFF, mapped=Command.STILL)