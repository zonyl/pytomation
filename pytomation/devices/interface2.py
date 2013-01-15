import random

from pytomation.utility.timer import Timer as CTimer
from .state2 import State2Device, State2

class Interface2Device(State2Device):
    
    def __init__(self, address=None, *args, **kwargs):
        self._address = address
        super(Interface2Device, self).__init__(*args, **kwargs)
        
        
    def _initial_vars(self, *args, **kwargs):
        super(Interface2Device, self)._initial_vars(*args, **kwargs)
        self._interfaces=[]
        self._sync = False
        self._sync_timer = None
        self._read_only = False
        self._send_always = False
    
    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value
        return self._address
    
    def _add_device(self, device):
        try:
            device.onCommand(device=self) # Register with the interface to receive events
            self._interfaces.append(device)
            return True
        except Exception, ex:
            return super(Interface2Device, self)._add_device(device)

    def _delegate_command(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        original = kwargs.get('original', None)
        if not self._read_only:
            for interface in self._interfaces:
                if source != interface and original != interface:
                    if not self._send_always and self._previous_state != self._command_to_state(command, None):
                        try:
                            if isinstance(command, tuple):
                                getattr(interface, command[0])(self._address, *command[1:])
                            else:
                                getattr(interface, command)(self._address)
                        except Exception, ex:
                            self._logger.error("{name} Could not send command '{command}' to interface '{interface}'".format(
                                                                                                name=self.name,
                                                                                                command=command,
                                                                                                interface=interface.name
                                                                                                                         ))
                else:
                    self._logger.debug("{name} is already at this state {state} for command {command}, do not send to interface".format(
                                                                                                name=self.name,
                                                                                                state=self.state,
                                                                                                command=command,
                                                                                                                  ))
        return super(Interface2Device, self)._delegate_command(command, *args, **kwargs)
        
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
        
    def read_only(self, value=None):
        if value:
            self._read_only=value
        return self._read_only
    
    def send_always(self, value=False):
        if value:
            self._send_always = value
        return self._send_always