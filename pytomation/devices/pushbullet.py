#Limited support for PushBullet
# by texnofobix
# based off the Google_Voice and Kodi

import requests
import json

from pytomation.devices import StateDevice, State
from pytomation.interfaces import Command


class PushBullet(StateDevice):
    STATES = [State.UNKNOWN, State.ON, State.OFF]
    COMMANDS = [Command.MESSAGE]
    
    _baseuri = 'https://api.pushbullet.com/v2'
    version = '0.0.1'

    def __init__(self, pbAccessToken=None, *args, **kwargs):
        self._headers = {'user-agent': 'PytomationPushBullet/' + self.version,
			'Authorization': 'Bearer ' + pbAccessToken
			}
        super(PushBullet, self).__init__(*args, **kwargs)

    def _ping(self):
	r = requests.get(self._baseuri + '/users/me',headers=self._headers)
	if r.status_code != 200:
	    print r.text
	    #print r.json
	    return False
	return True

    def pushNote(self,title="Blank",body="Blank"):
	self._headers['content-type'] = 'application/json'
	reqbody = {u'body': body, u'type': u'note', u'title': title}

	r = requests.post(self._baseuri + '/pushes',headers=self._headers, data=json.dumps(reqbody))
	
	if r.status_code != 200:
	    print r.text
	    #print r.json
	    return False
	return True

    def _delegate_command(self, command, *args, **kwargs):
        self._logger.debug('Delegating')
        self._logger.debug(str(args) + ":" + str(kwargs))
        if isinstance(command, tuple) and command[0] == Command.MESSAGE:
            self._logger.debug('Sending Message')
	    self.pushNote(title=command[1],body=command[2])
        super(PushBullet, self)._delegate_command(command, *args, **kwargs)
