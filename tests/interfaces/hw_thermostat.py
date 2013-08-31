import time

from unittest import TestCase

from tests.common import MockInterface
from pytomation.interfaces import HTTP, HW_Thermostat, HTTP

class HW_ThermostatInterfaceTests(TestCase):
    def setUp(self):
        self.host = '192.168.13.210'
        self.i = HTTP('http', self.host)
        self.interface = HW_Thermostat(self.i, self.host)

    def test_instantiation(self):
        self.assertIsInstance(self.interface, HW_Thermostat)
        
    def test_circulate(self):
        self.interface.off(self.host)
        time.sleep(5)
        self.interface.circulate(self.host)