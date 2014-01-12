import time

from unittest import TestCase

from pytomation.interfaces import HarmonyHub

class HarmonyHubTests(TestCase):
    def setUp(self):
        self.interface = HarmonyHub(address='192.168.13.134', 
                                    port='5222',
                                    user='jason@sharpee.com',
                                    password='password'
                                    )

    def test_instantiation(self):
        self.assertIsInstance(self.interface, HarmonyHub)
    
    def test_on(self):
        result = self.interface.on('Watch Roku')
        self.assertEqual(result, None)
        
    def test_off(self):
        result = self.interface.off('Doesnt matter')
        
    def test_get_config(self):
        print str(self.interface.get_config())
        