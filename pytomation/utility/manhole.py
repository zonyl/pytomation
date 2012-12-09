##################### TELNET MANHOLE ##########################
from twisted.internet import reactor
from twisted.manhole import telnet

from pytomation.common.system import *

class Manhole(object):
    def createShellServer(self ):
        print 'Creating shell server instance'
        factory = telnet.ShellFactory()
        port = reactor.listenTCP( 2000, factory)
        for instance_id, instance_detail in get_instances_detail():
            factory.namespace.update(
                {instance_detail['name']: instance_detail['instance']},
                {instance_id: instance_detail['instance']}
                )
        factory.username = 'pyto'
        factory.password = 'mation'
        print 'Listening on port 2000'
        return port

    def start(self):
        reactor.callWhenRunning( self.createShellServer )
        reactor.run()