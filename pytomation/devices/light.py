from .interface import InterfaceDevice
from .state import State

class Light(InterfaceDevice):
    def _initial_vars(self):
        super(Light, self)._initial_vars()
        self._restricted = False

    def _state_map(self, state, previous_state=None, source=None):
        mapped_state = state
        if state in (State.OPEN, State.DARK, State.MOTION) and not self._restricted:
            mapped_state = State.ON
        elif state in (State.CLOSED, State.LIGHT, State.STILL):
            mapped_state = State.OFF
        else:
            mapped_state = super(Light, self)._state_map(state, previous_state, source)
        # Restrict On/Off based on an attached device sending in LIGHT/DARK
        if state == State.LIGHT:
            self._restricted = True
        elif state == State.DARK:
            self._restricted = False
        return mapped_state