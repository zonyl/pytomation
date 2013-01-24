from unittest import TestCase

from pytomation.common.pytomation_api import PytomationAPI

class PytomationAPITests(TestCase):
    def setUp(self):
        self.api = PytomationAPI()
    
    def test_instantiation(self):
        self.assertIsNotNone(self.api)
        
    def test_device_invalid(self):
        response = self.api.get_response(method='GET', path="junk/test")
        self.assertEqual(response, 'null')
        
    def test_device_list(self):
        response = self.api.get_response(method='GET', path="devices")
        self.assertTrue('"PytomationAPI1"' in response)
        
        