"""
Interface Device:
"""
from .state import StateDevice, State
from pytomation.utility import CronTimer
from ..interfaces.common import *

class InterfaceDevice(StateDevice):
    
    def __init__(self, address=None, devices=(), *args, **kwargs):
        self._init(address=address, devices=devices, *args, **kwargs)
        super(InterfaceDevice, self).__init__(devices=devices, *args, **kwargs)

    def _init(self, *args, **kwargs):
        self._devices = []
        self.address = kwargs['address']
        self.interface = None
    	self._read_only = False

    def __setattr__(self, name, value):
        if name in self.STATES:
            self.interface.command.setattr(name, value)
        super(InterfaceDevice, self).__setattr__(name, value)

    def _set_state(self, state, previous_state=None, source=None):
        result = super(InterfaceDevice, self)._set_state(state, previous_state=previous_state, source=source)
        if self.interface and not self._read_only:
            try:
                getattr(self.interface, self._state)(self.address)
            except AttributeError, ex:
                pylog(__name__, "Interface ({interface}) doesn't support the State->Command: {state}".format(
                                                                                                            interface=self.interface,
                                                                                                            state=state,
                                                                                                            )
                      )
        return result

    def _on_command(self, address=None, command=None, source=None):
        if address == self.address:
            return super(InterfaceDevice, self)._set_state(command, source=source)

    def _bind_devices(self, devices):
        for device in devices:
            # bind any interfaces
            try:
                device.onCommand(address=self.address, callback=self._on_command)
                self.interface = device
            except Exception, ex:
                pass
        return super(InterfaceDevice, self)._bind_devices(devices)
