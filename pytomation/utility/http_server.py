import BaseHTTPServer

from SimpleHTTPServer import SimpleHTTPRequestHandler
from pytomation.common import config


file_path = "/tmp"

class PytomationHandlerClass(SimpleHTTPRequestHandler):
    def __init__(self,req, client_addr, server):
        self._request = req
        self._address = client_addr,
        self._server = server
        
        SimpleHTTPRequestHandler.__init__(self, req, client_addr, server)
    
    def translate_path(self, path):
        global file_path
        path = file_path + path
        return path

    def do_GET(self):
        return SimpleHTTPRequestHandler.do_GET(self)

#        response_html = "test"
#        self.send_response(200)
#        self.send_header("Content-type", "text/html")
#        self.send_header("Content-length", len(response_html))
#        self.end_headers()
#        self.wfile.write(response_html)
    
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

