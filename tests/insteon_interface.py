import select
import time

from unittest import TestCase, main

from pytomation.interfaces import InsteonPLM, Serial, HACommand, MockInterface, \
                                    TCP, Conversions


class InsteonInterfaceTests(TestCase):
    useMock = False

    def setUp(self):
        self.ms = MockInterface()
        if self.useMock:  # Use Mock Serial Port
            self.insteon = InsteonPLM(self.ms)
        else:
            # If we are running live, the insteon interface doesnt like to be bombarded with requests
#            time.sleep(3)
#            self.serial = Serial('/dev/ttyUSB0', 4800)
#            self.insteon = InsteonPLM(self.serial)
            self.tcp = TCP('192.168.13.146', 9761)
            self.insteon = InsteonPLM(self.tcp)

        self.insteon.start()

    def tearDown(self):
        self.insteon.shutdown()
        self.serial = None
        if self.tcp:
            self.tcp.shutdown()
            self.tcp = None

    def test_instantiation(self):
        self.assertIsNotNone(self.insteon,
                             'Insteon interface could not be instantiated')
        print 'instanc'

    def test_get_firmware_version(self):
        """
        >0000   02 60    .`
        <0000   02 60 16 F9 EC 03 05 92 06    .`.......
        """
        self.ms.add_response({Conversions.hex_to_ascii('0260'):
                                  Conversions.hex_to_ascii('026016F9EC03059206')})

        info = self.insteon.getPLMInfo()
        self.assertEqual(info['firmwareVersion'], "92")
        #select.select([], [], [])

if __name__ == '__main__':
    main()
