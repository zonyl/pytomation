from .interface import InterfaceDevice
from .state import State

class Photocell(InterfaceDevice):
    STATES = [State.UNKNOWN, State.LIGHT, State.DARK]

    def _init(self, *args, **kwargs):
        super(Photocell, self)._init(*args, **kwargs)
        self._read_only = True
       
    def _state_map(self, state, previous_state=None, source=None):
        if state == State.ON:
            mapped_state = State.DARK
        elif state == State.OFF:
            mapped_state = State.LIGHT
        else:
            mapped_state = super(Photocell, self)._state_map(state, previous_state, source)
        return mapped_state
