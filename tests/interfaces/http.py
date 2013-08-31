import os, time

from unittest import TestCase

from pytomation.interfaces import HTTP

class HTTPTests(TestCase):
    def setUp(self):
        self.interface = HTTP
        self._protocol = 'http'
        self._host = "www.google.com"
        
        self.interface = HTTP(protocol=self._protocol, host=self._host)
            
    def test_instance(self):
        self.assertIsNotNone(self.interface)
        
    def test_read(self):
        response = self.interface.read()
        self.assertIn("google", response)
        
    def test_write(self):
        response = self.interface.write("", None, "POST")
        self.assertIn("google", response)
