import time

from unittest import TestCase
from mock import Mock
from pytomation.interfaces import TCP, MHSend


class MHSendTests(TestCase):
    
    def setUp(self):
#        self.tcp = TCP('127.0.0.1', 8044)
        self.tcp = Mock()
        self.mh = MHSend(self.tcp)
        self.assertIsNotNone(self.mh)

    def test_send_voice_command(self):
        self.mh.voice('turn family lamp on')
        self.tcp.write.assert_called_with('run\x0Dturn family lamp on\x0D')
