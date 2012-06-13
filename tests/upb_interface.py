from unittest import TestCase, main

from pytomation import UPBInterface


class UPBInterfaceTests(TestCase):

    def setUp(self):
        self.upb = UPBInterface(serial='/dev/ttyS0')

    def test_factory(self):
        self.assertIsNotNone(self.upb,
                             'UPB interface could not be instantiated')

    def test_firware(self):
        pass

if __name__ == '__main__':
    main()
