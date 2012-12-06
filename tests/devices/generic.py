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