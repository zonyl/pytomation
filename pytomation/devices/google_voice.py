from googlevoice import Voice
#from googlevoice.util import input


from pytomation.devices import StateDevice, State
from pytomation.interfaces import Command

class Google_Voice(StateDevice):
    STATES = [State.UNKNOWN, State.ON, State.OFF]
    COMMANDS = [Command.MESSAGE]

    def __init__(self, user=None, password=None, *args, **kwargs):
        self._user = user
        self._password = password
        print "big"
        self._create_connection(user, password)
        super(Google_Voice, self).__init__(*args, **kwargs)

    def _create_connection(self, user, password):
        print "ehehe"
        self._voice = Voice()
        print 'user' + user + ":" + password
        self._voice.login(email=user, passwd=password)

    def _initial_vars(self, *args, **kwargs):
        super(Google_Voice, self)._initial_vars(*args, **kwargs)

    def _delegate_command(self, command, *args, **kwargs):
        self._logger.debug('Delegating')
        print 'pie'
        print str(args) + ":" + str(kwargs)
        if isinstance(command, tuple) and command[0] == Command.MESSAGE:            
            self._logger.debug('Sending Message')
            self._voice.send_sms(command[1], command[2])
            
        super(Google_Voice, self)._delegate_command(command, *args, **kwargs)

        
    