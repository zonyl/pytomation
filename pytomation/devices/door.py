from .interface import InterfaceDevice
from .state import State

class Door(InterfaceDevice):
    STATES = [State.UNKNOWN, State.OPEN, State.CLOSED]
       
    def _state_map(self, state, previous_state=None, source=None):
        if state == State.ON:
            mapped_state = State.OPEN
        elif state == State.OFF:
            mapped_state = State.CLOSED
        else:
            mapped_state = super(Door, self)._state_map(state, previous_state, source)
        return mapped_state
