"""
Pytomation Web socket server

Author(s):
David Heaps - king.dopey.10111@gmail.com
"""

import mimetypes
import os
import base64
import collections

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
        if message:
            self.ws.send(self._api.get_response(data=message, type=self._api.WEBSOCKET))

    def on_close(self, reason):
        print("WebSocket Client disconnected: ")


class PytoWebSocketServer(HAInterface):
    _api = PytomationAPI()

    def __init__(self, *args, **kwargs):
        self._address = kwargs.get('address', config.http_address)
        self._port = kwargs.get('port', int(config.http_port))
        self._path = kwargs.get('path', config.http_path)
        super(PytoWebSocketServer, self).__init__(self._address, *args, **kwargs)
        self.unrestricted = True  # To override light object restrictions

    def _init(self, *args, **kwargs):
        self._ssl_path = None
        self.ws = None
        try:
            self._ssl_path = config.ssl_path
        except:
            pass
        super(PytoWebSocketServer, self)._init(*args, **kwargs)

    def run(self):
        resource = collections.OrderedDict()
        resource['/api/bridge'] = PytoWebSocketApp
        resource['/api/device*'] = self.api_app
        resource['/api/voice'] = self.api_app
        resource['/'] = self.http_file_app
        if self._ssl_path:            
            self.ws = WebSocketServer(
            (self._address, self._port),
            Resource(resource),
            pre_start_hook=auth_hook, keyfile=self._ssl_path + '/server.key', certfile=self._ssl_path + '/server.crt')
        else:
            self.ws = WebSocketServer(
                (self._address, self._port),
                Resource(resource),
                pre_start_hook=auth_hook)

        print "Serving WebSocket Connection on", self._address, "port", self._port, "..."
        StateDevice.onStateChangedGlobal(self.broadcast_state)
        self.ws.serve_forever()

    def api_app(self, environ, start_response):
        method = environ['REQUEST_METHOD'].lower()
        if method == 'post':
            data = environ['wsgi.input'].read()
        else:
            data = None
        start_response("200 OK", [("Content-Type", "text/html"), ('Access-Control-Allow-Origin', '*')])
        return self._api.get_response(path='/'.join(environ['PATH_INFO'].split('/')[2:]), source=PytoWebSocketServer,
                                      method=method, data=data)

    def http_file_app(self, environ, start_response):
        path_info = environ['PATH_INFO']
        http_file = self._path + path_info
        if self._ssl_path:
            protocol = 'https://'
        else:
            protocol = 'http://'

        if os.path.exists(http_file):
            if os.path.isdir(http_file):
                if http_file.endswith('/'):
                    http_file += 'index.html'
                else:
                    if path_info.startswith('/'):
                        location = protocol + self._address + ':' + str(self._port) + path_info + '/'
                    else:
                        location = protocol + self._address + ':' + str(self._port) + '/' + path_info + '/'
                    start_response("302 Found",
                                   [("Location", location), ('Access-Control-Allow-Origin', '*')])
                    return ''

            mime = mimetypes.guess_type(http_file)
            start_response("200 OK", [("Content-Type", mime[0]), ('Access-Control-Allow-Origin', '*')])
            return open(http_file, "rb")
        else:
            start_response("404 Not Found", [("Content-Type", "text/html"), ('Access-Control-Allow-Origin', '*')])
            return "404 Not Found"

    def broadcast_state(self, state, source, prev, device):
        # TODO: add queue system and separate thread to avoid blocking on long network operations
        if self.ws:
            for client in self.ws.clients.values():
                message = self._api.get_state_changed_message(state, source, prev, device)
                client.ws.send(message)


def auth_hook(web_socket_handler):
    if config.auth_enabled == 'Y':
        auth = web_socket_handler.headers.get('Authorization', None)
        if not auth:
            if web_socket_handler.command == 'OPTIONS':
                web_socket_handler.start_response("200 OK",
                                                  [("Access-Control-Allow-Headers", "Authorization"),
                                                   ('Access-Control-Allow-Origin', '*')])
            else:
                web_socket_handler.start_response("401 Unauthorized", [('WWW-Authenticate', 'Basic realm=\"Pytomation\"'), ('Access-Control-Allow-Origin', '*')])
        elif auth != 'Basic ' + base64.b64encode(config.admin_user + ":" + config.admin_password):
            web_socket_handler.start_response("401 Unauthorized", [('WWW-Authenticate', 'Basic realm=\"Pytomation\"'), ('Access-Control-Allow-Origin', '*')])
        else:
            return False
    else:
        return False