import BaseHTTPServer

from SimpleHTTPServer import SimpleHTTPRequestHandler
import pytomation.common.config 
from pytomation.common.pyto_logging import PytoLogging
from pytomation.common.pytomation_api import PytomationAPI

file_path = "/tmp"

class PytomationHandlerClass(SimpleHTTPRequestHandler):
    def __init__(self,req, client_addr, server):
#        self._request = req
#        self._address = client_addr
#        self._server = server
        self._logger = PytoLogging(self.__class__.__name__)
        self._api = PytomationAPI()

        SimpleHTTPRequestHandler.__init__(self, req, client_addr, server)
    
    def translate_path(self, path):
        global file_path
        path = file_path + path
        return path

    def do_GET(self):
        self.route()

    def do_POST(self):
        self.route()

    def do_PUT(self):
        self.route()
        
    def do_DELETE(self):
        self.route()

    def do_ON(self):
        self.route()
        
    def do_OFF(self):
        self.route()

    def route(self):
        p = self.path.split('/')
        method = self.command
#        print "pd:" + self.path + ":" + str(p[1:])
        if p[1].lower() == "api":
            data = None
            if method.lower() == 'post':
                length = int(self.headers.getheader('content-length'))
                data = self.rfile.read(length)
#                print 'rrrrr' + str(length) + ":" + str(data)
                self.rfile.close()
            response = self._api.get_response(method=method, path="/".join(p[2:]), type=None, data=data)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(response))
            self.end_headers()
            self.wfile.write(response)
            self.finish()
        else:
            getattr(SimpleHTTPRequestHandler, "do_" + self.command.upper())(self)

class PytomationHTTPServer(object):
    def __init__(self, address="127.0.0.1", port=8080, path="/tmp", *args, **kwargs):
        global file_path
        self._address = address
        self._port = port
        self._protocol = "HTTP/1.0"
        self._path = path
        file_path = path
        
    def start(self):
        server_address = (self._address, self._port)
        
        PytomationHandlerClass.protocol_version = self._protocol
        httpd = BaseHTTPServer.HTTPServer(server_address, PytomationHandlerClass)
        
        sa = httpd.socket.getsockname()
        print "Serving HTTP files at ", self._path, " on", sa[0], "port", sa[1], "..."
        httpd.serve_forever()
        #BaseHTTPServer.test(HandlerClass, ServerClass, protocol)

