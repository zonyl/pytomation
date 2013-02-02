from pytomation.devices import State, StateDevice
from pytomation.interfaces import Command

class Room(StateDevice):
    STATES = [State.UNKNOWN, State.OCCUPIED, State.UNOCCUPIED]
    COMMANDS = [Command.OCCUPIED, Command.UNOCCUPIED]