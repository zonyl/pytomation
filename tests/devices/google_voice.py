from unittest import TestCase, main
from mock import Mock

from pytomation.devices import State, Google_Voice, StateDevice
from pytomation.interfaces import Command

class Google_VoiceTests(TestCase):
    def setUp(self):
        self.gv = Google_Voice(user='jason@sharpee.com', password='password')
    
    def test_instantiation(self):
        self.assertIsInstance(self.gv, Google_Voice)

    def test_send(self):
        self.gv.command((Command.MESSAGE, '7777777777', 'This is the test'))
