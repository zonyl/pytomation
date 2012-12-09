import re
##################### TELNET MANHOLE ##########################
from twisted.internet import reactor
from twisted.manhole import telnet

from pytomation.common.system import *

class Manhole(object):
    """
    Create a telnet server that allows you to reference your pytomation objects
    directly.  All objects names will be converted to lowercase and spaces will
    be converted to underscore _ .
    """    
    def createShellServer(self, user='pyto', password='mation', port=2000 ):
        print 'Creating shell server instance'
        factory = telnet.ShellFactory()
        port = reactor.listenTCP( port, factory)
        for instance_id, instance_detail in get_instances_detail().iteritems():
            name = re.sub('[\s]','_', instance_detail['name'].lower())
            factory.namespace.update(
                {
                    name: instance_detail['instance'],
                    instance_id: instance_detail['instance']
                }
                )
        factory.username = user
        factory.password = password
        print 'Listening on port '  + str(port)
        return port

    def start(self, user='pyto', password='mation', port=2000):
        reactor.callWhenRunning( self.createShellServer, user, password, port)
        reactor.run()