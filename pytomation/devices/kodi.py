# Based off the Google_Voice code
from xbmcjson import XBMC

from pytomation.devices import StateDevice, State
from pytomation.interfaces import Command


class Kodi(StateDevice):
    STATES = [State.UNKNOWN, State.ON, State.OFF]
    COMMANDS = [Command.MESSAGE]

    def __init__(self, host=None, *args, **kwargs):
        self._create_connection(host, *args, **kwargs)
        super(Kodi, self).__init__(*args, **kwargs)

    def _create_connection(self, host, *args, **kwargs):
        self._kodi = XBMC(host)
        #self._kodi.JSONRPC.Ping()

    def _initial_vars(self, *args, **kwargs):
        super(Kodi, self)._initial_vars(*args, **kwargs)

    def _delegate_command(self, command, *args, **kwargs):
        self._logger.debug('Delegating')
        self._logger.debug(str(args) + ":" + str(kwargs))
        if isinstance(command, tuple) and command[0] == Command.MESSAGE:
            self._logger.debug('Sending Message')
            self._kodi.GUI.ShowNotification(title=command[1], message = command[2])
        super(Kodi, self)._delegate_command(command, *args, **kwargs)
