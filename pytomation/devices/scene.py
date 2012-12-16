from .interface import InterfaceDevice
from .state import State

class Scene(InterfaceDevice):
    STATES = [State.UNKNOWN, State.ACTIVE, State.INACTIVE]

    def __init__(self, address=None, devices=(), *args, **kwargs):
        super(Scene, self).__init__(address=address, devices=devices, *args, **kwargs)
        self._get_controlled_devices(devices)
        
    def _init(self, *args, **kwargs):
        super(Scene, self)._init(*args, **kwargs)
        self._can_update = kwargs.get('update', False)
        self._controlled_devices = {}

    def _state_map(self, state, previous_state=None, source=None):
        mapped = super(Scene, self)._state_map(state=state, previous_state=previous_state, source=source)
        if mapped not in self.STATES:
            if mapped == State.ON:
                mapped = State.ACTIVE
            elif mapped == State.OFF:
                mapped = State.INACTIVE
            else:
                mapped = State.UNKNOWN
        return mapped


    def _get_controlled_devices(self, devices):
        for device in devices:
            try:
                for k, v in device.iteritems():
                    self._controlled_devices.update({k: v})
            except Exception, ex:
                pass

        if self._can_update:
            try:
                self.interface.update_scene(self.address, devices=self._controlled_devices )
            except Exception, ex:
                self._logger.warning("{name} Interface {interface} does not support updating scenes for {address}".format(
                                                                        name=self.name,
                                                                        interface=self.interface.name,
                                                                        address=self.address,
                                                                        ))


    
#    def _call_interface_method(self, interface_method):
#        return interface_method(self.address, self.controlled_devices)