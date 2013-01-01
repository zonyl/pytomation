from .interface2 import Interface2Device
from .state2 import State2
from ..interfaces import Command

class Light2(Interface2Device):
    STATES = [State2.UNKNOWN, State2.ON, State2.OFF, State2.LEVEL]
    COMMANDS = [Command.ON, Command.OFF, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL]

    def _initial_vars(self, *args, **kwargs):
        super(Light2, self)._initial_vars(*args, **kwargs)
        self._restricted = False
        self.mapped(command=Command.MOTION, mapped=Command.ON)
        self.mapped(command=Command.DARK, mapped=Command.ON)
        self.mapped(command=Command.OPEN, mapped=Command.ON)
        self.mapped(command=Command.STILL, mapped=Command.OFF)
        self.mapped(command=Command.LIGHT, mapped=Command.OFF)
        self.mapped(command=Command.CLOSE, mapped=Command.OFF)

    def command(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        if source and source.state == State2.DARK:
            self.restricted = False
        elif source and source.state == State2.LIGHT:
            self.restricted = True
        super(Light2, self).command(command, *args, **kwargs)

    def _command_state_map(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        (m_state, m_command) = super(Light2, self)._command_state_map(command, *args, **kwargs)
        if source and not source == self and m_command == Command.ON and \
            source.state in (State2.OPEN, State2.MOTION, State2.DARK):
            if self.restricted:
                m_command = None
                m_state = None 
                self._logger.info("{name} is restricted. Ignoring command {command} from {source}".format(
                                                                                     name=self.name,
                                                                                     command=command,
                                                                                     source=source.name,
                                                                                                           ))

        return (m_state, m_command)
        
    @property
    def restricted(self):
        return self._restricted
    
    @restricted.setter
    def restricted(self, value):
        self._restricted = value
        return self._restricted