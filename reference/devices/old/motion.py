from .interface import InterfaceDevice
from .state import State

class Motion(InterfaceDevice):
    STATES = [State.UNKNOWN, State.MOTION, State.STILL]

    def _init(self, *args, **kwargs):
	super(Motion, self)._init(*args, **kwargs)
	self._read_only = True
       
    def _state_map(self, state, previous_state=None, source=None):
        if state == State.ON:
            mapped_state = State.MOTION
        elif state == State.OFF:
            mapped_state = State.STILL
        else:
            mapped_state = super(Motion, self)._state_map(state, previous_state, source)
        return mapped_state
