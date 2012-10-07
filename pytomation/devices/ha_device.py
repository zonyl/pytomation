

class HADevice(object):
    STATES = ['on','off','unknown']

    _state = None
    _delegates = {}

    def __init__(self, interface=None, address=None):
        self.interface = interface
        self.address = address
        self._state = 'unknown'
        self._prev_state = 'unknown'

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        return self._state
    
    def __getattr__(self, name):
        #state functions
        if name.lower() in [ n.lower() for n in self.STATES]:
            if name == name.upper():
                return name.lower()
            else:
                return lambda: self._set_state(name)
        elif name[0:3] == 'on_':
            return lambda x: self._add_delegate(name[3:len(name)], x)
        raise AttributeError

    def __setattr__(self, name, value):
        if name in self.STATES:
            self.interface.command.setattr(name, value)
            self._state = name
        else:
            super(HADevice, self).__setattr__(name, value)

    def _set_state(self, name):
        getattr(self.interface, name)(self.address)
        self._state = name
        self._delegate(name)
        self._prev_state = self._state
        return True

    def _add_delegate(self, name, callback):
        state_list = self._delegates.get(name, None)
        if state_list:
            state_list.append(callback)
        else:
            self._delegates[name] = [callback]
        return True
    
    def _delegate(self, name):
        delegate_list = self._delegates.get(name, None)
        if delegate_list:
            for delegate in delegate_list:
                delegate(state=name, previous_state=self._prev_state, source=self)
                