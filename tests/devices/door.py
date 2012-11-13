
from unittest import TestCase, main
from mock import Mock

from pytomation.devices import Door


class DoorTests(TestCase):
    
    def setUp(self):
        self.interface = Mock()
        self.device = Door('D1', self.interface)

    def test_instantiation(self):
        self.assertIsNotNone(self.device,
                             'Door Device could not be instantiated')


if __name__ == '__main__':
    main() 