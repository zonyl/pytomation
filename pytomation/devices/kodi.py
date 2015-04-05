# Based off the Google_Voice code
from xbmcjson import XBMC,PLAYER_VIDEO

from pytomation.devices import StateDevice, State
from pytomation.interfaces import Command


class Kodi(StateDevice):
    STATES = [State.UNKNOWN, State.ON, State.OFF]
    COMMANDS = [Command.MESSAGE, Command.STATUS]

    def __init__(self, host=None, *args, **kwargs):
        self._create_connection(host, *args, **kwargs)
        super(Kodi, self).__init__(*args, **kwargs)

    def _create_connection(self, host, *args, **kwargs):
        self._kodi = XBMC(host)
        #self._kodi.JSONRPC.Ping()

    def _initial_vars(self, *args, **kwargs):
	self._set_state(value="idle" )
        super(Kodi, self)._initial_vars(*args, **kwargs)

    def _delegate_command(self, command, *args, **kwargs):
        self._logger.debug('Delegating')
        self._logger.debug(str(args) + ":" + str(kwargs))
	    
        if isinstance(command, tuple) and command[0] == Command.MESSAGE:
            self._logger.debug('Sending Message')
            self._kodi.GUI.ShowNotification(title=command[1], message = command[2])
	if command == Command.STATUS:
	    self._getStatus()
	#if command == Command.STOP:
	    #print "Stop called"
	    #self._kodi.Player.Stop([PLAYER_VIDEO])
	#if command == Command.PLAYPAUSE:
	    #status = self._kodi.Player.PlayPause([PLAYER_VIDEO])
	    #status['result']['speed']  
	    
        super(Kodi, self)._delegate_command(command, *args, **kwargs)

    def _getStatus(self):
	try:
	    self._set_state(value=self._kodi.Player.GetItem([PLAYER_VIDEO])['result']['item']['label'] )
	except KeyError:
	    self._set_state(value="idle" )
	

#>>> xbmc.Player.GetItem([PLAYER_VIDEO])
#{u'jsonrpc': u'2.0', u'id': 11, u'result': {u'item': {u'type': u'movie', u'label': u'Insertion Sort in Python (from YouTube)'}}}

#>>> xbmc.Player.PlayPause([PLAYER_VIDEO]) #pause when 0
#{u'jsonrpc': u'2.0', u'id': 12, u'result': {u'speed': 0}}

#>>> xbmc.Player.PlayPause([PLAYER_VIDEO]) #play when 1
#{u'jsonrpc': u'2.0', u'id': 13, u'result': {u'speed': 1}}

