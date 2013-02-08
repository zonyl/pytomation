from pytomation.devices import State, StateDevice
from pytomation.interfaces import Command

class Room(StateDevice):
    STATES = [State.UNKNOWN, State.OCCUPIED, State.VACANT]
    COMMANDS = [Command.OCCUPY, Command.VACATE]
    
    def _initial_vars(self, *args, **kwargs):
        super(Room, self)._initial_vars(*args, **kwargs)
        self._restricted = False
        self.mapped(command=Command.MOTION, mapped=Command.OCCUPY)
        self.mapped(command=Command.OPEN, mapped=Command.OCCUPY)
        self.mapped(command=Command.STILL, mapped=None)
        self.mapped(command=Command.CLOSE, mapped=Command.VACATE)

    def command(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        if command == Command.OCCUPY and source and getattr(source, 'state') and source in self._devices and source.state == State.OCCUPIED:
            return super(Room, self).command(command=Command.VACATE, *args, **kwargs)
        if command == Command.VACATE and source and getattr(source, 'state') and source in self._devices and source.state == State.VACANT:
#            return super(Room, self).command(command=Command.OCCUPY, *args, **kwargs)
            return True
        return super(Room, self).command(command=command, *args, **kwargs)
