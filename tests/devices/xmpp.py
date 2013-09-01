from unittest import TestCase, main
from mock import Mock

from pytomation.devices import State, XMPP, StateDevice
from pytomation.interfaces import Command

class XMPPTests(TestCase):
    def setUp(self):
        self.xmpp = XMPP(id='jason@sharpee.com', password='password', server='talk.google.com', port=5222)
    
    def test_instantiation(self):
        self.assertIsInstance(self.xmpp, XMPP)

    def test_send(self):
        self.xmpp.command((Command.MESSAGE, 'jason@sharpee.com', 'This is the test'))
