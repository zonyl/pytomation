from unittest import TestCase, main
from mock import Mock

from pytomation.devices import State2Device
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

    def test_type_id(self):
        
        device = StateDevice(name='Test')
        self.assertIsNotNone(device.type_id)
        
    def test_device_type_name(self):
        name = "Test"
        device = StateDevice(name=name)
        self.assertEqual(device.type_name, "StateDevice")