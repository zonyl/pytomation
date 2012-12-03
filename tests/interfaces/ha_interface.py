
from unittest import TestCase, main

from pytomation.interfaces import HAInterface
from mock import Mock

class HAInterfaceTests(TestCase):
    def setUp(self):
        
        self.interface = HAInterface(Mock())
        
    def test_instances(self):
        prev = len(self.interface.instances)
        interface = HAInterface(Mock())
        self.assertTrue(len(interface.instances) > prev)