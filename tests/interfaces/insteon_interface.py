import select
import time

from binascii import unhexlify
from unittest import TestCase, main
from mock import Mock

from tests.common import MockInterface, Mock_Interface, Command
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

    def test_insteon_receive_status(self):
        """
        [2013/09/07 15:24:51] [DEBUG] [InsteonPLM] Receive< 0000   02 50 23 D2 BE 00 00 01 CB 11 00    .P#........
        d395e51a11bb096e20f9ae84b47f8884
        
        [2013/09/07 15:24:51] [WARNING] [InsteonPLM] Unhandled packet (couldn't find any pending command to deal with it) 
        [2013/09/07 15:24:51] [WARNING] [InsteonPLM] This could be a status message from a broadcast
        [2013/09/07 15:24:51] [DEBUG] [InsteonPLM] Running status request..........
        [2013/09/07 15:24:51] [DEBUG] [InsteonPLM] Command: 23.D2.BE 19 00
        [2013/09/07 15:24:51] [DEBUG] [InsteonPLM] Queued bff1ddfd362ac6ef71555d959edbb90a
        [2013/09/07 15:24:53] [DEBUG] [InsteonPLM] Timed out for bff1ddfd362ac6ef71555d959edbb90a - Requeueing (already had 0 retries)
        [2013/09/07 15:24:53] [DEBUG] [InsteonPLM] Interesting.  timed out for bff1ddfd362ac6ef71555d959edbb90a, but there are no pending com$
        [2013/09/07 15:24:53] [DEBUG] [InsteonPLM] Removing Lock <thread.lock object at 0x1a7f030>
        [2013/09/07 15:24:53] [DEBUG] [InsteonPLM] Transmit>026223d2be0f1900
        [2013/09/07 15:24:53] [DEBUG] [InsteonPLM] Receive< 0000   02 50 23 D2 BE 22 FF 5B 41 11 01    .P#..".[A..
        4996cf7dd3a4b4722f120dc9c0fe5b17
        
        [2013/09/07 15:24:53] [WARNING] [InsteonPLM] Unhandled packet (couldn't find any pending command to deal with it)
        [2013/09/07 15:24:53] [WARNING] [InsteonPLM] This could be a status message from a broadcast
        [2013/09/07 15:24:53] [DEBUG] [InsteonPLM] Running status request..........
        [2013/09/07 15:24:53] [DEBUG] [InsteonPLM] Command: 23.D2.BE 19 00
        
        """
        global logging_default_level
        ## Default logging level
        #logging_default_level = "DEBUG"
        m = Mock_Interface()
#        m.diabled.return_value = False
        i = InsteonPLM(m)
        self._result = False
        i.onCommand(self._insteon_receive_status_callback, '23.D2.BE')
        m.put_read_data(Conversions.hex_to_ascii('025023D2BE000001CB1100'))
        time.sleep(1)
        # Transmits: 026223d2be0f1900
        m.put_read_data(Conversions.hex_to_ascii('025023D2BE22FF5B411101'))
        time.sleep(3)
        self.assertEqual(self._result, True)

    def _insteon_receive_status_callback(self, *args, **kwargs):
        command = kwargs.get('command', None)
        print 'command:' + command
        if command == Command.ON:
            self._result = True

    def test_insteon_status(self):
        response = self.insteon.status('44.33.22')
        self.assertEqual(response, True)

if __name__ == '__main__':
    main()
