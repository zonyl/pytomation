import time

from unittest import TestCase

from tests.common import MockInterface, Mock_Interface
from pytomation.interfaces import NestThermostat
from pytomation.devices import Thermostat

class NestThermostatTests(TestCase):
    def setUp(self):
        self.host = '192.168.13.210'
#        self.i = HTTP('http', self.host)
        self.i = Mock_Interface()
#        self.interface = Nest(self.i, self.host)
        self.interface = NestThermostat(username='user@email.com', password='password')
    
    def test_instantiation(self):
        self.assertIsInstance(self.interface, NestThermostat)
        
    def test_setpoint(self):
        #Address = (Structure ID, Device ID)
        address = (123, 34)
        self.interface.level(address, 74)
        
        
    def test_circulate(self):
        #Address = (Structure ID, Device ID)
        address = (123, 34)
        self.interface.circulate(address)
        
    def test_thermostat_setpoint(self):
        d = Thermostat(address=(123,123), devices=self.interface, name='Thermo1')
        d.level(74)

        