import select
import time

from binascii import unhexlify
from unittest import TestCase, main
from mock import Mock

from tests.common import MockInterface
from pytomation.interfaces import InsteonPLM, Serial, HACommand, \
                                    TCP, Conversions


class InsteonInterfaceTests(TestCase):
    useMock = True

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

        #self.insteon.start()

    def tearDown(self):
        self.insteon.shutdown()
        self.serial = None
        try:
            self.tcp.shutdown()
            self.tcp = None
        except:
            pass

    def test_instantiation(self):
        self.assertIsNotNone(self.insteon,
                             'Insteon interface could not be instantiated')

    def test_get_firmware_version(self):
        """
        >0000   02 60    .`
        <0000   02 60 16 F9 EC 03 05 92 06    .`.......
        """
        self.ms.add_response({Conversions.hex_to_ascii('0260'):
                                  Conversions.hex_to_ascii('026016F9EC03059206')})

        info = self.insteon.getPLMInfo()
#        self.assertEqual(info['firmwareVersion'], "92")
        #select.select([], [], [])

    def test_device_on(self):
        """
        Transmit>
        0000   02 62 19 05 7B 0F 11 FF    .b..{...
        <  0000   02 62 19 05 7B 0F 11 FF 06    .b..{....
        <  0000   02 50 19 05 7B 16 F9 EC 2B 11 FF    .P..{...+..
        """
        self.ms.add_response({Conversions.hex_to_ascii('026219057B0F11FF'):
                              Conversions.hex_to_ascii('026219057B0F11FF06') + \
                              Conversions.hex_to_ascii('025019057B16F9EC2B11FF')})
        response = self.insteon.on('19.05.7b')
        #time.sleep(4000)
        self.assertEqual(response, True)
        
    def test_insteon_level2(self):
        m = Mock()
        m.disabled.return_value = False
        i = InsteonPLM(m)
        i.level('12.20.B0', 50)
        #todo: figure out how to really deal with this race condition
        time.sleep(3)
        m.write.assert_called_with(unhexlify('02621220b00f117f'))

if __name__ == '__main__':
    main()
