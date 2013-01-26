from unittest import TestCase

from pytomation.common.pytomation_api import PytomationAPI
from pytomation.devices import StateDevice, State
from pytomation.interfaces import Command

class PytomationAPITests(TestCase):
    def setUp(self):
        self.api = PytomationAPI()
    
    def test_instantiation(self):
        self.assertIsNotNone(self.api)
        
    def test_device_invalid(self):
        response = self.api.get_response(method='GET', path="junk/test")
        self.assertEqual(response, 'null')
        
    def test_device_list(self):
        d=StateDevice(name='device_test_1')
        d.on()
        response = self.api.get_response(method='GET', path="devices")
        self.assertTrue('"name": "device_test_1"' in response)
    
    def test_device_get(self):
        d=StateDevice(name='device_test_1')
        d.on()
        response = self.api.get_response(method='GET', path="device/" + str(d.type_id))
        self.assertTrue('"name": "device_test_1"' in response)
        
    def test_device_on(self):
        d=StateDevice(name='device_test_1')
        d.off()
        self.assertEqual(d.state, State.OFF)
        response = self.api.get_response(method='ON', path="device/" + str(d.type_id))
        self.assertEqual(d.state, State.ON)
        self.assertTrue('"name": "device_test_1"' in response)
        