"""
Pytomation Web socket server

Author(s):
David Heaps - king.dopey.10111@gmail.com
"""

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from .ha_interface import HAInterface
from pytomation.common.pytomation_api import PytomationAPI
from pytomation.common import config
from pytomation.devices import StateDevice

class PytoWebSocketApp(WebSocketApplication):
    _api = PytomationAPI()

    def on_open(self):
        print "WebSocket Client connected"

    def on_message(self, message):
        pass
        #todo: Future plain text (voice) command hook

    def on_close(self, reason):
        print("WebSocket Client disconnected: ")

class PytoWebSocketServer(HAInterface):
    _api = PytomationAPI()

    def __init__(self, address=None, port=None, path=None, *args, **kwargs):
        super(PytoWebSocketServer, self).__init__(address, *args, **kwargs)
        self.unrestricted = True # To override light object restrictions
        self.ws = None

    def _init(self, *args, **kwargs):
        self._address = kwargs.get('address', config.http_address)
        self._port = kwargs.get('port', int(config.http_port) + 10)
        super(PytoWebSocketServer, self)._init(*args, **kwargs)

    def run(self):
        server_address = (self._address, self._port)

        """
        todo: Add pre_start_hook for header access and authentication
        todo: For SSL (possibly check for existence), pass  **ssl_args
            {   "certfile": "[path to mycert.crt]"),
                "keyfile": "[path to mykey.key]"),
            }
        """
        self.ws = WebSocketServer(
            server_address,
            Resource({'/api/state': PytoWebSocketApp, '/api/device*': self.api_app, '/': self.http_file_app})
        )

        print "Serving WebSocket Connection on", self._address, "port", self._port, "..."
        StateDevice.onStateChanged(self.broadcast_state)
        self.ws.serve_forever()

    def api_app(self, environ, start_response):
        method = environ['REQUEST_METHOD'].lower()
        if method == 'post':
            data = environ['wsgi.input'].read()
        else:
            data = None
        start_response("200 OK", [("Content-Type", "text/html"), ('Access-Control-Allow-Origin', '*')])
        return self._api.get_response(path='/'.join(environ['PATH_INFO'].split('/')[2:]), source=PytoWebSocketServer,
                                      method=method, data=data, type=self._api.WEBSOCKET)

    def http_file_app(self, environ, start_response):
        #todo: send web app files
        start_response("200 OK", [("Content-Type", "text/html"), ('Access-Control-Allow-Origin', '*')])
        path = environ['PATH_INFO']
        return path

    def broadcast_state(self, state, source, prev, device):
        #todo: add queue system and separate thread to avoid blocking on long network operations
        if self.ws:
            for client in self.ws.clients.values():
                message = self._api.get_state_changed_message(state, source, prev, device)
                client.ws.send(message)