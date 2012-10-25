from .state import StateDevice, State

class Location(StateDevice):
    STATES = [State.LIGHT, State.DARK]

    class MODE():
        STANDARD = 'standard'
        CIVIL = 'civil'
        NAUTICAL = 'nautical'
        ASTRONOMICAL = 'astronomical'
        
    _mode = MODE.STANDARD
    
    def __init__(self, latitude, longitude, mode=None):
        self._latitude = latitude
        self._longitudue = longitude
        if mode:
            self._mode = mode

    @property
    def mode(self):
        return self._mode
    
    @mode.setter
    def mode(self, value):
        self._mode = value
        self._evaluate()

    def _evaluate(self):
        pass
