import BaseHTTPServer

from SimpleHTTPServer import SimpleHTTPRequestHandler
from pytomation.common import config

file_path = "/tmp"

class PytomationHandlerClass(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        return file_path + "/" + path
    
class PytomationHTTPServer(object):
    def __init__(self, address="127.0.0.1", port=8080, path="/tmp", *args, **kwargs):
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
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        httpd.serve_forever()
        #BaseHTTPServer.test(HandlerClass, ServerClass, protocol)
