import ssl

try:
    import xmpp
except:
    pass
import re
import time

from pytomation.devices import Door, StateDevice, State
from pytomation.interfaces import Command

class XMPP_Client(StateDevice):
    STATES = [State.UNKNOWN, State.ON, State.OFF]
    COMMANDS = [Command.MESSAGE]

    def __init__(self, *args, **kwargs):
        self._xmpp = None
        super(XMPP_Client, self).__init__(*args, **kwargs)

    def _initial_vars(self, *args, **kwargs):
        super(XMPP_Client, self)._initial_vars(*args, **kwargs)
        self._xmpp_id = kwargs.get('id',None)
        self._password = kwargs.get('password', None)
        self._server = kwargs.get('server', None)
        self._port = kwargs.get('port', None)

        if not self._xmpp:
            self._logger.info('Connecting to server for id:{id} ({server})'.format(
                                                   id=self._xmpp_id,
                                                   server=self._server,
                                                                                   ))
            status = None
            jid = xmpp.JID(self._xmpp_id)
            self._xmpp = xmpp.Client(jid.getDomain())
            self.connect()
            self._logger.info("Connection Result: {0}".format( status))
            result = self._xmpp.auth(re.match('(.*)\@.*', self._xmpp_id).group(1), self._password,'TESTING')
            #self._xmpp.sendInitPresence()   
            self._logger.debug('Processing' + str(result))
        else:
            self._logger.debug('Here twice?')

    def connect(self):
        status = None
        if self._server:
            status = self._xmpp.connect(server=(self._server,self._port))
        else:
            status = self._xmpp.connect()
        return status

    def _delegate_command(self, command, *args, **kwargs):
        self._logger.debug('Delegating')

        if isinstance(command, tuple) and command[0] == Command.MESSAGE:            
            self._logger.debug('Sending Message')
#             result = self._xmpp.send_message(mto=command[1],
#                                       mbody=command[2],
#                                       mtype='chat')
            message = xmpp.Message( command[1] ,command[2]) 
            message.setAttr('type', 'chat')
            try:
                self._xmpp.send(message )
            except IOError, ex:
                try:
                    self.connect()
                    self._xmpp.send(message )
                except IOError, ex1:
                    self._logger.error('Could not reconnect:' + str(ex1))
                except Exception, ex1:
                    self._logger.error('Could not reconnect error:' + str(ex1))
            except Exception, ex:
                self._logger.error('Unknown Error: ' + str(ex))
                
#            time.sleep(5)
        super(XMPP_Client, self)._delegate_command(command, *args, **kwargs)

        
    