import select

from unittest import TestCase, main

from pytomation.interfaces import UPB, Serial, HACommand, MockInterface


class UPBInterfaceTests(TestCase):
    useMock = True

    def setUp(self):
        self.ms = MockInterface()
        if self.useMock:  # Use Mock Serial Port
            self.upb = UPB(self.ms)
        else:
            self.serial = Serial('/dev/ttyUSB0', 4800)
            self.upb = UPB(self.serial)

        self.upb.start()

    def tearDown(self):
        self.upb.shutdown()
        self.serial = None

    def test_instantiation(self):
        self.assertIsNotNone(self.upb,
                             'UPB interface could not be instantiated')

    def test_get_firmware_version(self):
        # What will be written / what should we get back
        self.ms.add_response({'\x120202FC\x0D': 'PR021234\x0D'})

        response = self.upb.get_register(2, 2)
        self.assertEqual(response, '1234')
#        if self.useMock:
#            self.assertEqual(self.ms._written, '\x120202FC\x0D')
        #sit and spin, let the magic happen
        #select.select([], [], [])

    def test_device_on(self):
        """
        UPBPIM, myPIM, 49, 0x1B08, 30
        UPBD,   upb_foyer,      myPIM,  49, 3
        Response>  Foyer Light On
        0000   50 55 30 38 31 30 33 31    PU081031
        0008   30 33 31 45 32 32 36 34    031E2264
        0010   31 30 0D                   10.
        """
        self.ms.add_response({'\x14081031031E226410\x0D': 'PA\x0D'})
        # Network / Device ID
        response = self.upb.on((49, 3))
        self.assertTrue(response)

    def test_multiple_commands_at_same_time(self):
        """
        Response>
        0000   50 55 30 38 31 30 33 31    PU081031
        0008   31 32 31 45 32 32 30 30    121E2200
        0010   36 35 0D 50 55 30 38 31    65.PU081
        0018   30 33 31 31 32 31 45 32    031121E2
        0020   32 30 30 36 35 0D          20065.
        """
if __name__ == '__main__':
    main()
