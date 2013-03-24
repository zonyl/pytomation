from pytomation.devices import InterfaceDevice, State
from pytomation.interfaces import Command

class Generic(InterfaceDevice):
    STATES = [State.UNKNOWN, State.OFF, State.ON, State.ACTIVE, State.INACTIVE, State.MOTION, State.STILL, State.LIGHT, State.DARK, State.OPEN, State.CLOSED]
    COMMANDS = [Command.ON, Command.OFF, Command.ACTIVATE, Command.DEACTIVATE, Command.MOTION, Command.STILL,
                Command.LIGHT, Command.DARK, Command.OPEN, Command.CLOSE, Command.LEVEL, Command.AUTOMATIC, Command.MANUAL, Command.STATUS]
    
    