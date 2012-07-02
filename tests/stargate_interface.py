import select

from unittest import TestCase, main

from pytomation.interfaces import Stargate, Serial, HACommand, MockInterface


class StargateInterfaceTests(TestCase):
    useMock = False

    def setUp(self):
        self.ms = MockInterface()
        if self.useMock:  # Use Mock Serial Port
            self.sg = Stargate(self.ms)
        else:
            self.serial = Serial('/dev/ttyUSB0', 9600)
            self.sg = Stargate(self.serial)

        self.sg.start()

    def tearDown(self):
        self.sg.shutdown()
        self.serial = None

    def test_instantiation(self):
        self.assertIsNotNone(self.sg,
                             'SG interface could not be instantiated')

    def test_digital_input(self):
        """
        digital input #1 ON
        !!07/01083237a0fe
        digital input #1 OFF
        !!07/01083239a0ff
        """
        # What will be written / what should we get back
        self.ms.add_response({'\x120202FC\x0D': 'PR021234\x0D'})

        #response = self.sg.get_register(2, 2)
        #self.assertEqual(response, '1234')
#        if self.useMock:
#            self.assertEqual(self.ms._written, '\x120202FC\x0D')
        #sit and spin, let the magic happen
        #select.select([], [], [])

if __name__ == '__main__':
    main()
