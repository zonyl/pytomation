from .interface import InterfaceDevice
from .state import State

class Door(InterfaceDevice):
    STATES = [State.UNKNOWN, State.OPEN, State.CLOSED]
    
    def _set_state(self, state, previous_state=None, source=None):
        if state == State.OPEN:
            mapped_state = State.ON
        else:
            mapped_state = State.OFF
        super(Door, self)._set_state(mapped_state, previous_state, source)
        
    def _on_command(self, address, state):
        if state == State.ON:
            mapped_state = State.OPEN
        else:
            mapped_state = State.OFF
        super(Door, self)._on_command(address, mapped_state)