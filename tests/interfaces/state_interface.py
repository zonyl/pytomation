import time

from unittest import TestCase
from mock import Mock

from pytomation.interfaces import StateInterface
from pytomation.devices import Interface2Device, State2

class StateIntefaceTests(TestCase):
    def setUp(self):
        self._response = None

    def test_receive_state(self):
        mi = Mock()
        mi.read = self.response
        interface = StateInterface(mi)
        device = Interface2Device(address=None,
                                 devices=interface, 
                                 initial_state=State2.UNKNOWN)
        self.assertEqual(device.state, State2.UNKNOWN)
        self._response = State2.ON
        time.sleep(2)
        self.assertEqual(device.state, State2.ON)
        
        
    def response(self, *args, **kwargs):
        if self._response:
            resp = self._response
            self._response = None
            return resp
        else:
            return ''
        