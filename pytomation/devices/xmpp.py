import ssl

from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream import cert

from pytomation.devices import Door, StateDevice, State
from pytomation.interfaces import Command

class XMPP(StateDevice):
    STATES = [State.UNKNOWN, State.ON, State.OFF]
    COMMANDS = [Command.MESSAGE]

    def __init__(self, *args, **kwargs):
        self._xmpp = None
        super(XMPP, self).__init__(*args, **kwargs)

    def _initial_vars(self, *args, **kwargs):
        super(XMPP, self)._initial_vars(*args, **kwargs)
        self._xmpp_id = kwargs.get('id',None)
        self._password = kwargs.get('password', None)
        self._server = kwargs.get('server', None)
        self._port = kwargs.get('port', None)

        if not self._xmpp:
            self._xmpp = ClientXMPP(self._xmpp_id, self._password)
    
            self._xmpp.add_event_handler("session_start", self._session_start)
            self._xmpp.add_event_handler("message", self._message)
            self._xmpp.add_event_handler("ssl_invalid_cert", self._invalid_cert)
    
            self._logger.info('Connecting to server for id:{id} ({server})'.format(
                                                   id=self._xmpp_id,
                                                   server=self._server,
                                                                                   ))
            status = None
            if self._server or self._port:
                status = self._xmpp.connect((self._server, self._port))
            else:
                status = self._xmpp.connect()
            self._logger.info("Connection Result: {0}".format( status))
    
            self._xmpp.process(block=False)
            self._logger.debug('Processing')
        else:
            self._logger.debug('Here twice?')
        
    def _session_start(self, event):
        self._logger.debug('Session Start')
        self._xmpp.send_presence()
        self._xmpp.get_roster()
        self._logger.debug('Session End')
        
    def _message(self, msg):
        self._logger.debug('REceived Message')
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()


    def _invalid_cert(self, pem_cert):
        self._logger.debug('Cert')
        der_cert = ssl.PEM_cert_to_DER_cert(pem_cert)
        try:
            cert.verify('talk.google.com', der_cert)
            self._logger.debug("CERT: Found GTalk certificate")
        except cert.CertificateError as err:
            self._logger.error(err.message)
            self.disconnect(send_close=False)
        self._logger.debug('Cert End')

    def _delegate_command(self, command, *args, **kwargs):
        self._logger.debug('Delegating')

        if isinstance(command, tuple) and command[0] == Command.MESSAGE:            
            self._logger.debug('Sending Message')
            result = self._xmpp.send_message(mto=command[1],
                                      mbody=command[2],
                                      mtype='chat')
        super(XMPP, self)._delegate_command(command, *args, **kwargs)

        
    