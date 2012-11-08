"""
Interface Device:
"""
from .state import StateDevice, State
from pytomation.utility import CronTimer


class InterfaceDevice(StateDevice):
    
    def __init__(self, address=None, *devices):
        self._devices = []
        self.address = address
        super(InterfaceDevice, self).__init__(*devices)

    def __setattr__(self, name, value):
        if name in self.STATES:
            self.interface.command.setattr(name, value)
        super(InterfaceDevice, self).__setattr__(name, value)

    def _set_state(self, state):
        getattr(self.interface, state)(self.address)
        return super(InterfaceDevice, self)._set_state(state)
    
    def _on_command(self, address, state):
        if address == self.address:
            return super(InterfaceDevice, self)._set_state(state)

    def _bind_devices(self, devices):
        for device in devices:
            # bind any interfaces
            try:
                device.onCommand(address=self.address, callback=self._on_command)
            except Exception, ex:
                pass
        return super(InterfaceDevice, self)._bind_devices(devices)