from unittest import TestCase

from pytomation.devices import Generic, State


class GenericTests(TestCase):
    def setUp(self):
        self.device = Generic('asd')

    def test_instantiation(self):
        self.assertIsNotNone(self.device)

    def test_on(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.on()
        self.assertEqual(self.device.state, State.ON)
    
    def test_still(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.still()
        self.assertEqual(self.device.state, State.STILL)
        
    def test_open(self):
        self.assertEqual(self.device.state, State.UNKNOWN)
        self.device.open()
        self.assertEqual(self.device.state, State.OPEN)
        
        