from .interface import InterfaceDevice
from .state import State

class Light(InterfaceDevice):
    def _state_map(self, state, previous_state=None, source=None):
        mapped_state = state
        if state in (State.OPEN, State.DARK, State.MOTION):
            mapped_state = State.ON
        elif state in (State.CLOSED, State.LIGHT, State.STILL):
            mapped_state = State.OFF
        else:
            mapped_state = super(Light, self)._state_map(state, previous_state, source)
        return mapped_state