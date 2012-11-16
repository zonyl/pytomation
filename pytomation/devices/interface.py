"""
Interface Device:
"""
from .state import StateDevice, State
from pytomation.utility import CronTimer


class InterfaceDevice(StateDevice):
    
    def __init__(self, address=None, devices=(), initial_state=None):
        self._devices = []
        self.address = address
        self.interface = None
        super(InterfaceDevice, self).__init__(devices=devices, initial_state=initial_state)

    def __setattr__(self, name, value):
        if name in self.STATES:
            self.interface.command.setattr(name, value)
        super(InterfaceDevice, self).__setattr__(name, value)

    def _set_state(self, state, previous_state=None, source=None):
        result = super(InterfaceDevice, self)._set_state(state, previous_state=previous_state, source=source)
        if self.interface:
            getattr(self.interface, self._state)(self.address)
        return result

    def _on_command(self, address, state):
        if address == self.address:
            return super(InterfaceDevice, self)._set_state(state)

    def _bind_devices(self, devices):
        for device in devices:
            # bind any interfaces
            try:
                device.onCommand(address=self.address, callback=self._on_command)
                self.interface = device
            except Exception, ex:
                pass
        return super(InterfaceDevice, self)._bind_devices(devices)