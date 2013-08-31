from pytomation.devices import InterfaceDevice, State
from pytomation.interfaces import Command

class Thermostat(InterfaceDevice):
    STATES = [State.UNKNOWN, State.OFF, State.HEAT, State.COOL, State.LEVEL, State.CIRCULATE, State.AUTOMATIC]
    COMMANDS = [Command.AUTOMATIC, Command.COOL, Command.HEAT, Command.OFF, Command.LEVEL, Command.STATUS, Command.CIRCULATE, Command.STILL]
