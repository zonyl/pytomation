from unittest import TestCase

from pytomation.common.pytomation_api import PytomationAPI

class PytomationAPITests(TestCase):
    def setUp(self):
        self.api = PytomationAPI()
    
    def test_instantiation(self):
        self.assertIsNotNone(self.api)
        
    def test_device_list(self):
        response = self.api.get_response(method='GET', path="/api/devices")
        self.assertIsNotNone(response)
        self.assertTrue(response.contains("Content-type"))