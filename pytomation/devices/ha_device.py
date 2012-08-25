

class HADevice(object):
    _state = None

    def __init__(self, interface=None, address=None):
        self.interface = interface
        self.address = address

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        return self._state

    @property
    def UNKNOWN(self):
        return self._state

    @property
    def ON(self):
        return True

    @property
    def OFF(self):
        return False

    def on(self):
        self.interface.on(self.address)
        self._state = self.ON
        return True

    def off(self):
        self.interface.off(self.address)
        self._state = self.OFF
        return True
