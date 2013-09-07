import time

from unittest import TestCase

from pytomation.interfaces import WeMo

class WeMoTests(TestCase):
    def setUp(self):
#        self.interface = WeMo( '192.168.13.141', '49153')
        self.interface = WeMo( '192.168.13.141', '49153')

    def test_instantiation(self):
        self.assertIsInstance(self.interface, WeMo)
    
    def test_on(self):
        result = self.interface.on()
        self.assertEqual(result, None)