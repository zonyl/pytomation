import select

from unittest import TestCase, main

from pytomation.interfaces import UPB, Serial, HACommand


class UPBInterfaceTests(TestCase):

    def setUp(self):
        self.serial = Serial('/dev/ttyUSB0', 4800)
        self.upb = UPB(self.serial)
        self.upb.start()

    def test_instantiation(self):
        self.assertIsNotNone(self.upb,
                             'UPB interface could not be instantiated')

    def test_get_firmware_version(self):
#        self.assertIsNone(self.upb.command('29', HACommand.ON))
        self.upb.get_register()
        #sit and spin, let the magic happen
        select.select([], [], [])

if __name__ == '__main__':
    main()
