
from unittest import TestCase, main

from pytomation.interfaces import HAInterface
from mock import Mock

class HAInterfaceTests(TestCase):
    def setUp(self):
        di = Mock()
        self.interface = HAInterface(di)
        
    def test_instances(self):
        prev = len(self.interface.instances)
        interface = HAInterface(Mock())
        self.assertTrue(len(interface.instances) > prev)
        
    def test_update_status(self):
        device = Mock()
        device.address.return_value = 'a1'
        self.interface.onCommand(device=device)
#        self.interface.status = Mock()
#        self.interface.status.return_value = lambda x: x
        self.interface.update_status()
#        self.interface.status.assert_called_with(address='a1')
        