from unittest import TestCase, main
from mock import Mock

from pytomation.devices import State, XMPP_Client, StateDevice
from pytomation.interfaces import Command

class XMPP_ClientTests(TestCase):
    def setUp(self):
        self.xmpp = XMPP_Client(id='pytomation@sharpee.com', password='password', server='talk.google.com', port=5222)
    
    def test_instantiation(self):
        self.assertIsInstance(self.xmpp, XMPP_Client)

    def test_send(self):
        self.xmpp.command((Command.MESSAGE, 'jason@sharpee.com', 'This is the test'))
