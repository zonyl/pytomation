
from unittest import TestCase, main

from tests.common import MockInterface
from pytomation.devices import Light


class LightTests(TestCase):

    def setUp(self):
        self.interface = MockInterface()
        self.device = Light(interface=self.interface, address='D1')

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Light Device could not be instantiated')

    def test_on(self):
        self.assertEqual(self.device.state, self.device.UNKNOWN)
        self.device.on()
        self.assertEqual(self.device.state, self.device.ON)

if __name__ == '__main__':
    main() 