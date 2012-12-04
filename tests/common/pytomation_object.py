
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import StateDevice
from pytomation.interfaces import UPB

class PytomationObjectTests(TestCase):
    def test_interface_name(self):
        name = "Main UPB"
        interface = Mock()
        interface.read.return_value = ""
        upb = UPB(interface, name=name)
        self.assertEqual(upb.name, name)
        
    def test_device_name(self):
        name = "Front Outlet"
        device = StateDevice(name=name)
        self.assertEqual(device.name, name)
        