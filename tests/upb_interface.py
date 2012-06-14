from unittest import TestCase, main

from pytomation.interfaces import UPBInterface, Serial, HACommand


class UPBInterfaceTests(TestCase):

    def setUp(self):
        self.serial = Serial('/dev/ttyUSB0')
        self.upb = UPBInterface(self.serial)

    def test_instantiation(self):
        self.assertIsNotNone(self.upb,
                             'UPB interface could not be instantiated')

    def test_get_firmware_version(self):
        self.assertIsNone(self.upb.command('29', HACommand.ON))

if __name__ == '__main__':
    main()
