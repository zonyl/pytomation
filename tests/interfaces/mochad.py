from unittest import TestCase
from mock import Mock
from pytomation.interfaces import TCP, Mochad

class MochadTests(TestCase):
    
    def setUp(self):
#        self.tcp = TCP('127.0.0.1', 1099)
        self.tcp = Mock()
        self.mochad = Mochad(self.tcp)
        self.assertIsNotNone(self.mochad)

    def test_on(self):
        self.mochad.on('a1')
        self.tcp.write.assert_called_with('pl a1 on\x0D')
        