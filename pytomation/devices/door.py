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
            mapped_state = state
        return mapped_state

#    def _on_command(self, address, state):
#        if state == State.ON:
#            mapped_state = State.OPEN
#        else:
#            mapped_state = State.OFF
#        return super(Door, self)._on_command(address, mapped_state)