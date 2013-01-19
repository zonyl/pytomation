from unittest import TestCase

from pytomation.devices import Generic2, State2


class Generic2Tests(TestCase):
    def setUp(self):
        self.device = Generic2('asd')

    def test_instantiation(self):
        self.assertIsNotNone(self.device)

    def test_on(self):
        self.assertEqual(self.device.state, State2.UNKNOWN)
        self.device.on()
        self.assertEqual(self.device.state, State2.ON)