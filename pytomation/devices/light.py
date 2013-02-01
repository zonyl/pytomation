from .interface import InterfaceDevice
from .state import State
from ..interfaces import Command

class Light(InterfaceDevice):
    STATES = [State.UNKNOWN, State.ON, State.OFF, State.LEVEL]
    COMMANDS = [Command.ON, Command.OFF, Command.PREVIOUS, Command.TOGGLE, Command.INITIAL,
                Command.AUTOMATIC, Command.MANUAL]

    def _initial_vars(self, *args, **kwargs):
        super(Light, self)._initial_vars(*args, **kwargs)
        self._restricted = False
        self.mapped(command=Command.MOTION, mapped=Command.ON)
        self.mapped(command=Command.DARK, mapped=Command.ON)
        self.mapped(command=Command.OPEN, mapped=Command.ON)
        self.mapped(command=Command.STILL, mapped=Command.OFF)
        self.mapped(command=Command.LIGHT, mapped=Command.OFF)
        self.mapped(command=Command.CLOSE, mapped=Command.OFF)

    def command(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        if command == Command.LIGHT:
            a = 1
        try:
            if source and source.state == State.DARK:
                self.restricted = False
            elif source and source.state == State.LIGHT:
                self.restricted = True
        except AttributeError, ex:
            pass
        super(Light, self).command(command, *args, **kwargs)

    def _command_state_map(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        if command == Command.ON:
            a = 1
        (m_state, m_command) = super(Light, self)._command_state_map(command, *args, **kwargs)
        try:
            if source and not source == self and m_command == Command.ON and \
                getattr(source, 'state') and source.state in (State.OPEN, State.MOTION, State.DARK):
                if self.restricted:
                    m_command = None
                    m_state = None 
                    self._logger.info("{name} is restricted. Ignoring command {command} from {source}".format(
                                                                                         name=self.name,
                                                                                         command=command,
                                                                                         source=source.name,
                                                                                                               ))
        except AttributeError, ex:
            pass #source is not a state device
        return (m_state, m_command)
        
    @property
    def restricted(self):
        return self._restricted
    
    @restricted.setter
    def restricted(self, value):
        self._restricted = value
        return self._restricted