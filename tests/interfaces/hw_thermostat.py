import time

from unittest import TestCase

from tests.common import MockInterface, Mock_Interface
from pytomation.interfaces import HTTP, HW_Thermostat, HTTP

class HW_ThermostatInterfaceTests(TestCase):
    def setUp(self):
        self.host = '192.168.13.210'
#        self.i = HTTP('http', self.host)
        self.i = Mock_Interface()
        self.interface = HW_Thermostat(self.i, self.host)

    def test_instantiation(self):
        self.assertIsInstance(self.interface, HW_Thermostat)
        
    def test_circulate(self):
        self.interface.off(self.host)
        time.sleep(2)
        self.interface.circulate(self.host)
    
    def test_setpoint(self):
        self.interface.level(address=self.host, level=72)
        
    def test_cool(self):
        self.interface.cool()
        time.sleep(2)
        self.assertIn(('tstat', '{"tmode": 2}'), self.i.query_write_data())
        