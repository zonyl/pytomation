import select

from unittest import TestCase, main

from pytomation.interfaces import InsteonPLM, Serial, HACommand, MockInterface


class InsteonInterfaceTests(TestCase):
    useMock = True

    def setUp(self):
        self.ms = MockInterface()
        if self.useMock:  # Use Mock Serial Port
            self.upb = InsteonPLM(self.ms)
        else:
            self.serial = Serial('/dev/ttyUSB0', 4800)
            self.upb = InsteonPLM(self.serial)

        self.insteon.start()

    def test_instantiation(self):
        self.assertIsNotNone(self.upb,
                             'Insteon interface could not be instantiated')

    def test_get_firmware_version(self):
        response = self.upb.get_register(2, 2)
        self.assertEqual(response, '1234')

        #sit and spin, let the magic happen
        #select.select([], [], [])

if __name__ == '__main__':
    main()
