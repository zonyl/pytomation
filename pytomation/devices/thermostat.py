from pytomation.devices import InterfaceDevice, State
from pytomation.interfaces import Command

class Thermostat(InterfaceDevice):
    STATES = [State.UNKNOWN, State.OFF, State.ON, State.HEAT, State.COOL, State.LEVEL, State.CIRCULATE]
    COMMANDS = [Command.ON, Command.OFF, Command.AUTOMATIC,  Command.LEVEL, Command.AUTOMATIC, Command.COOL, Command.HEAT, Command.STATUS, Command.CIRCULATE]
