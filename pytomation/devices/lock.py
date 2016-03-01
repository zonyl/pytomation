from pytomation.devices import State, InterfaceDevice
from pytomation.interfaces import Command

class Lock(InterfaceDevice):
    STATES = [State.UNKNOWN, State.LOCKED, State.UNLOCKED]
    COMMANDS = [Command.LOCK, Command.UNLOCK, Command.TOGGLE, Command.STATUS]
    
    def _initial_vars(self, *args, **kwargs):
        super(Lock, self)._initial_vars(*args, **kwargs)
        self._restricted = False
        self._send_always = True