import select
import time

from unittest import TestCase, main

from tests.common import MockInterface
from pytomation.interfaces import Stargate, Serial, HACommand


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
        """
0000   21 21 30 38 2F 30 31 30    !!08/010
0008   38 31 39 33 30 61 30 66    81930a0f
0010   65                         e
"""
        # What will be written / what should we get back
        self.ms.add_response({'##%1d\r': '!!07/01083237a001\r\n'})

        # Register delegate
        self.sg.onCommand(callback=self._digital_input_callback, address='D1')
        # resend EchoMode to trigger response
        self.sg.echoMode()
        time.sleep(3)
        self.assertEqual(self.__digital_input_params['kwargs']['address'].upper(), 'D1')

    def test_digital_input_multiple(self):
        """
0000   21 21 30 38 2F 30 31 30    !!08/010
0008   37 38 38 30 37 61 30 66    78807a0f
0010   65 0D 0A 21 21 30 38 2F    e..!!08/
0018   30 31 30 37 38 38 30 37    01078807
0020   34 30 30 31 0D 0A 21 21    4001..!!
0028   30 38 2F 30 31 30 37 38    08/01078
0030   38 30 37 34 31 30 30 0D    8074100.
0038   0A                         .

"""
        # What will be written / what should we get back
        self.ms.add_response({'##%1d\r': '!!07/01083237a001\r\n!!07/01083237a000\r\n'})

        # Register delegate
        self.sg.onCommand(callback=self._digital_input_callback, address='D1')
        # resend EchoMode to trigger response
        self.sg.echoMode()
        time.sleep(1.5)
        self.assertEqual(self.__digital_input_params['kwargs']['address'].upper(), 'D1')


    def _digital_input_callback(self, *args, **kwargs):
        print "Args:" + str(args) + " Kwargs:" + str(kwargs)
        self.__digital_input_params = {'args': args, 'kwargs': kwargs}

        #response = self.sg.get_register(2, 2)
        #self.assertEqual(response, '1234')
#        if self.useMock:
#            self.assertEqual(self.ms._written, '\x120202FC\x0D')
        #sit and spin, let the magic happen
        #select.select([], [], [])

if __name__ == '__main__':
    main()
