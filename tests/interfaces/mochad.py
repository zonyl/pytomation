import time

from unittest import TestCase
from mock import Mock
from pytomation.interfaces import TCP, Mochad


class MochadTests(TestCase):
    
    def setUp(self):
#        self.tcp = TCP('127.0.0.1', 1099)
#        self.tcp = TCP('www.yahoo.com', 80)
        self.tcp = Mock()
        self.mochad = Mochad(self.tcp)
        self.assertIsNotNone(self.mochad)

    def test_on(self):
        self.mochad.on('a1')
        self.tcp.write.assert_called_with('pl a1 on\x0D')
        
    def test_receive_off(self):
        interface = Mock()
        interface.callback.return_value = True
        interface.read.return_value = ''
        m = Mochad(interface)
        m.onCommand(address='a1', callback=interface.callback)
        interface.read.return_value = "pl a1 off\x0D"
        time.sleep(2)
        interface.read.return_value = ''
        interface.callback.assert_called_with(address='a1', command='off', source=m)  
       
        