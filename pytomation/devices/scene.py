'''
File:
    scene.py

Description:
    A device that represents a Scene or group of devices.

Author(s): 
     Chris Van Orman

License:
    This free software is licensed under the terms of the GNU public license, Version 1     

Usage:

Example: 

Notes:

Created on Mar 11, 2013
'''
from .interface import InterfaceDevice
from pytomation.interfaces.common import Command
from .state import State

class Scene(InterfaceDevice):
    STATES = [State.UNKNOWN, State.ON, State.OFF]
    COMMANDS = [Command.ON, Command.OFF, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]

    def __init__(self, address=None, *args, **kwargs):
        super(Scene, self).__init__(address=address, *args, **kwargs)
        self._controllers = kwargs.get('controllers', [])
        self._responders = kwargs.get('responders', {})       
        
        self._processResponders(self._responders)

    def _initial_vars(self, *args, **kwargs):
        super(Scene, self)._initial_vars(*args, **kwargs)
        self._responders = {}
        self._controllers = []

    def addressMatches(self, address):
        matches = super(Scene, self).addressMatches(address)
        
        #check if any controller also matches
        for d in self._controllers:
            matches = matches or d.addressMatches(address)
        
        return matches

    def command(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        if source in self._responders:
            #if it was a responder, just update the scene state.
            self._updateState()
        elif source not in self._responders:
            super(Scene, self).command(command, *args, **kwargs)
            #The scene state changed, set the state of all responders.
            self._updateResponders(self.state)

    def _updateState(self):
        #set our state based on what the state of all responders are.
        state = State.ON
        for d,s in self._responders.items():
            state = State.OFF if d.state != s['state'] else state
        if state != self.state:
            self.state = state
            
    def _updateResponders(self, state):
        #set the state of our responders based upon the scene state.
        for d,s in self._responders.items():
            d.state = State.OFF if state == State.OFF else s['state']

    def _processResponders(self, responders):
        #attach to all the responders so we can update the Scene state when they change.
        for r in responders:
            r.on_command(self)
