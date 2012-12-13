from .interface import InterfaceDevice
from .state import State

class Light(InterfaceDevice):
    STATES = [State.UNKNOWN,
              State.ON,
              State.OFF,
              State.L10,
              State.L20,
              State.L30,
              State.L40,
              State.L50,
              State.L60,
              State.L70,
              State.L80,
              State.L90,
              ]

    def _initial_vars(self):
        super(Light, self)._initial_vars()
        self._restricted = False

    def _set_state(self, state, previous_state=None, source=None):
        if state == State.DARK:
            self._restricted = False
        super(Light, self)._set_state(state, previous_state, source)

    def _state_map(self, state, previous_state=None, source=None):
        mapped_state = state
        if state in (State.OPEN, State.DARK, State.MOTION):
            if not self._restricted:
                mapped_state = State.ON
            else:
                self._logger.info('{name} is currently restricted'.format(
                                                                          name=self._name,
                                                                          ))
                mapped_state = None
        elif state in (State.CLOSED, State.LIGHT, State.STILL):
            mapped_state = State.OFF
        else:
            mapped_state = super(Light, self)._state_map(state, previous_state, source)

        # Restrict On/Off based on an attached device sending in LIGHT/DARK
        if state == State.LIGHT:
            self._restricted = True
        elif state == State.DARK:
            self._restricted = False
            
        #check for delay:
        if state != mapped_state and self._delays.get(mapped_state, None) and \
            state not in (State.LIGHT, State.DARK):
            #ignore the mapped request for the state and let the timer take care of it
            #if someone sends us the direct state then we will assume it is manual and needed immediately
            #Allow photocells to skip delay
            self._logger.info('{name} we have a delay for this state = "{state}" mapped to "{mapped}"'.format(
                                                                                                              name=self.name,
                                                                                                              state=state,
                                                                                                              mapped=mapped_state))
            mapped_state = None
        return mapped_state