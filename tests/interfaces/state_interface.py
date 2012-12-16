import time

from unittest import TestCase
from mock import Mock

from pytomation.interfaces import StateInterface
from pytomation.devices import InterfaceDevice, State

class StateIntefaceTests(TestCase):
    def setUp(self):
        self._response = None

    def test_receive_state(self):
        mi = Mock()
        mi.read = self.response
        interface = StateInterface(mi)
        device = InterfaceDevice(address=None,
                                 devices=interface, 
                                 initial_state=State.UNKNOWN)
        self.assertEqual(device.state, State.UNKNOWN)
        self._response = State.ON
        time.sleep(2)
        self.assertEqual(device.state, State.ON)
        
        
    def response(self, *args, **kwargs):
        if self._response:
            resp = self._response
            self._response = None
            return resp
        else:
            return ''
        