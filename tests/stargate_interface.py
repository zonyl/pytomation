import select
import time

from unittest import TestCase, main

from pytomation.interfaces import Stargate, Serial, HACommand, MockInterface


class StargateInterfaceTests(TestCase):
    useMock = True

    def setUp(self):
        self.ms = MockInterface()
        if self.useMock:  # Use Mock Serial Port
            self.sg = Stargate(self.ms)
        else:
            self.serial = Serial('/dev/ttyUSB0', 2400)
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
        self.ms.add_response({'##%1d\r': '!!07/01083237a0fe'})

        # Register delegate
        self.sg.onCommand(callback=self._digital_input_callback, address='D1')
        # resend EchoMode to trigger response
        self.sg.echoMode()
        time.sleep(3)
        self.assertEqual(self.__digital_input_params['kwargs']['address'].upper(), 'D1')

    def _digital_input_callback(self, *args, **kwargs):
        self.__digital_input_params = {'args': args, 'kwargs': kwargs}

        #response = self.sg.get_register(2, 2)
        #self.assertEqual(response, '1234')
#        if self.useMock:
#            self.assertEqual(self.ms._written, '\x120202FC\x0D')
        #sit and spin, let the magic happen
        #select.select([], [], [])

if __name__ == '__main__':
    main()
