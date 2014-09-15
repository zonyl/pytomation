import json
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from .ha_interface import HAInterface
from pytomation.common.pytomation_api import PytomationAPI
from pytomation.common import config
from pytomation.devices import StateDevice

class PytoWebSocketApp(WebSocketApplication):
    #def __init__(self):
    #    self._api = PytomationAPI()

    def on_open(self):
        print "WebSocket Client connected"

    def on_message(self, message):
        pass
        #todo: Add run device command code

    def on_close(self, reason):
        print("WebSocket Client disconnected: ")

class PytoWebSocketServer(HAInterface):

    def __init__(self, address=None, port=None, path=None, *args, **kwargs):
        super(PytoWebSocketServer, self).__init__(address, *args, **kwargs)
        self.unrestricted = True # To override light object restrictions
        self.wss = None

    def _init(self, *args, **kwargs):
        self._address = kwargs.get('address', config.http_address)
        self._port = kwargs.get('port', int(config.http_port) + 10)
        super(PytoWebSocketServer, self)._init(*args, **kwargs)

    def run(self):
        server_address = (self._address, self._port)

        #todo: add pre_start_hook for header access and authentication
        self.wss = WebSocketServer(
            server_address,
            Resource({'/': PytoWebSocketApp})
        )

        print "Serving WebSocket Connection on", self._address, "port", self._port, "..."
        StateDevice.onStateChanged(self.broadcast_state)
        self.wss.serve_forever()

    def broadcast_state(self, state, source, prev, device):
        #todo: add queue system and separate thread to avoid blocking on long network operations
        if self.wss:
            for client in self.wss.clients.values():
                client.ws.send(json.dumps({
                    'id': device.type_id,
                    'name': device.name,
                    'type_name': device.type_name,
                    'state': state,
                    'previous_state': prev
                }))