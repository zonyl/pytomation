"""
Interface Device:
"""
import random

from .state import StateDevice, State
from pytomation.utility import CronTimer
from pytomation.utility.timer import Timer as CTimer
from ..interfaces.common import *


class InterfaceDevice(StateDevice):
    
    def __init__(self, address=None, devices=(), *args, **kwargs):
        self._init(address=address, devices=devices, *args, **kwargs)
        sync = kwargs.get('sync', None)
        if sync:
            self._sync = sync
        super(InterfaceDevice, self).__init__(devices=devices, *args, **kwargs)

    def _init(self, *args, **kwargs):
        self._devices = []
        self.address = kwargs['address']
        self.interface = None
        self._read_only = False
        self._sync = False

    def __setattr__(self, name, value):
        if name in self.STATES:
            self.interface.command.setattr(name, value)
        super(InterfaceDevice, self).__setattr__(name, value)

    def _set_state(self, state, previous_state=None, source=None):
        source_name = None
        if source:
            source_name = source._name
            
        result = super(InterfaceDevice, self)._set_state(state, previous_state=previous_state, source=source)
        # Only send if we have interface, we approved of the state change and are not readonly
        # do not send state "unknown"
        if self.interface and result and not self._read_only and self._state != State.UNKNOWN: 
            try:
                self._logger.info('{device} Sending "{state}" to interface: {interface}, from {source}'.format(
                                                                                     device=self._name,
                                                                                     state=self._state,
                                                                                     source=source_name,
                                                                                     interface=str(self.interface), 
                                                                                     r=result)
                                  )
                state_method = getattr(self.interface, self._state)
                if state_method:
                    result = state_method(self.address)
                else:
                    self._logger.error("Interface ({interface}) does not have the State '{state}' for address ({address})".format(
                                                                                    state=self._state,
                                                                                    address=self.address,
                                                                                    interface=str(self._interface),
                                                                                                         ))
                    
            except AttributeError, ex:
                self._logger.error('Interface ({interface}) does not support the State->Command: "{state}"'.format(
                                                                                                            interface=str(self.interface),
                                                                                                            state=self.state,
                                                                                                            )
                      )
            except Exception, ex:
                self._logger.critical('Interface ({interface}) suffered a critical error: {error}'.format(interface=str(self.interface),
                                                                                                          error=str(ex)))
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
    
    @property
    def sync(self):
        return self._sync
    
    @sync.setter
    def sync(self, value):
        self._sync = value
        if value:
            self._start_sync()
        else:
            self._stop_sync()
        return self._sync
    
    def _start_sync(self):
        # get a random number of secs from 30 minutes to an hour
        offset = random.randint(0, 30 * 60) + (30 * 60) 
        self._sync_timer = CTimer(offset)
        self._sync_timer.action(self._run_sync, ())
        self._sync_timer.start()        

    def _stop_sync(self):
        self._sync_timer.stop()
        
    def _run_sync(self):
        if self.interface:
            getattr(self.interface, self._state)()
        self._start_sync()
        