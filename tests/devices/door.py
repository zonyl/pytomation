
from unittest import TestCase, main

from pytomation.devices import Door
from pytomation.interfaces import MockInterface


class DoorTests(TestCase):

    def setUp(self):
        self.interface = MockInterface()
        self.device = Door(interface=self.interface, address='D1')

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Door Device could not be instantiated')

    def test_on(self):
        self.assertEqual(self.device.state, self.device.UNKNOWN)
        self.device.on()
        self.assertEqual(self.device.state, self.device.ON)

if __name__ == '__main__':
    main() 