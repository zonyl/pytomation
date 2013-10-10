import select
import time

from binascii import unhexlify
from unittest import TestCase, main
from mock import Mock

from tests.common import MockInterface, Mock_Interface, Command
from pytomation.interfaces import InsteonPLM, Serial, HACommand, \
                                    TCP, Conversions
from pytomation.devices import Door, Light, State

class InsteonInterfaceTests(TestCase):
    useMock = True

    def setUp(self):
        self.ms = Mock_Interface()
        self.insteon = InsteonPLM(self.ms)

# If we are running live, the insteon interface doesnt like to be bombarded with requests
#            time.sleep(3)
#            self.serial = Serial('/dev/ttyUSB0', 4800)
#            self.insteon = InsteonPLM(self.serial)
#            self.tcp = TCP('192.168.13.146', 9761)
#            self.insteon = InsteonPLM2(self.tcp)

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

    def test_device_on(self):
        """
        Transmit>
        0000   02 62 19 05 7B 0F 11 FF    .b..{...
        <  0000   02 62 19 05 7B 0F 11 FF 06    .b..{....
        <  0000   02 50 19 05 7B 16 F9 EC 2B 11 FF    .P..{...+..
        """
#        self.ms.add_response({Conversions.hex_to_ascii('026219057B0F11FF'):
#                              Conversions.hex_to_ascii('026219057B0F11FF06') + \
#                              Conversions.hex_to_ascii('025019057B16F9EC2B11FF')})
        response = self.insteon.on('19.05.7b')
        self.assertIn(Conversions.hex_to_ascii('026219057B0F11FF'), self.ms.query_write_data())
        self.ms.put_read_data(Conversions.hex_to_ascii('026219057B0F11FF06'))
        self.ms.put_read_data(Conversions.hex_to_ascii('025019057B16F9EC2B11FF'))
        time.sleep(2)
        self.assertEqual(response, True)
        
    def test_insteon_level2(self):
        self.ms.disabled = False
        
        self.insteon.level('12.20.B0', 50)
        #todo: figure out how to really deal with this race condition
        time.sleep(3)
        self.assertIn(unhexlify('02621220b00f117f'), self.ms.query_write_data())
#        self.ms.write.assert_called_with(unhexlify('02621220b00f117f'))

    def test_insteon_receive_status(self):
        """
[2013/10/09 19:56:54] [DEBUG] [InsteonPLM] Receive< 0000   02 50 23 D2 BE 00 00 01 CB 11 00    .P#........
d395e51a11bb096e20f9ae84b47f8884

[2013/10/09 19:56:54] [WARNING] [InsteonPLM] Unhandled packet (couldn't find any pending command to deal with it)
[2013/10/09 19:56:54] [WARNING] [InsteonPLM] This could be a status message from a broadcast
[2013/10/09 19:56:54] [DEBUG] [InsteonPLM] HandleStandDirect
[2013/10/09 19:56:54] [DEBUG] [InsteonPLM] Running status request:False:True:True:..........
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Command: 23.D2.BE 19 00
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Queued bff1ddfd362ac6ef71555d959edbb90a
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Transmit>026223d2be0f1900
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] TransmitResult>8
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Receive< 0000   02 50 23 D2 BE 22 FF 5B 41 11 01    .P#..".[A..
4996cf7dd3a4b4722f120dc9c0fe5b17

[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] ValidResponseCheck: 0000   53 44 31 39                SD19

[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] ValidResponseCheck2: {'callBack': <bound method InsteonPLM._handle_StandardDirect_LightSta$
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] ValidResponseCheck3: ['SD19']
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Valid Insteon Command COde: SD11
[2013/10/09 19:56:55] [WARNING] [InsteonPLM] Unhandled packet (couldn't find any pending command to deal with it)
[2013/10/09 19:56:55] [WARNING] [InsteonPLM] This could be a status message from a broadcast
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] HandleStandDirect
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Setting status for:23.D2.BE:17:1..........
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Received Command:23.D2.BE:on
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Delegates for Command: []
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Devices for Command: []
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Received Command:23.D2.BE:on
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Delegates for Command: []
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Devices for Command: []
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Received a Modem NAK! Resending command, loop time 0.400000
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Queued bff1ddfd362ac6ef71555d959edbb90a
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Received a Modem NAK! Resending command, loop time 0.600000
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Transmit>026223d2be0f1900
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] TransmitResult>8
[2013/10/09 19:56:55] [DEBUG] [InsteonPLM] Receive< 0000   02 50 23 D2 BE 11 01 01 CB 06 00    .P#........
0e3a2974df58ef76268f23a48ec650a9

        """
        global logging_default_level
        ## Default logging level
        #logging_default_level = "DEBUG"
        self._result = False
        self.insteon.onCommand(self._insteon_receive_status_callback, '23.D2.BE')
        self.ms.put_read_data(Conversions.hex_to_ascii('025023D2BE000001CB1100'))
        time.sleep(1)
        # Transmits: 026223d2be0f1900
        self.ms.put_read_data(Conversions.hex_to_ascii('025023D2BE22FF5B411101'))
        time.sleep(3)
        self.assertEqual(self._result, Command.ON)

    def _insteon_receive_status_callback(self, *args, **kwargs):
        command = kwargs.get('command', None)
        print 'command:' + command
        self._result = command

    def test_insteon_status(self):
        response = self.insteon.status('44.33.22')
        self.assertEqual(response, True)
        
    def test_insteon_receive_status2(self):
        """
Receive Broadcast OFF command from a remote device
[2013/10/07 20:37:42] [DEBUG] [InsteonPLM] Receive< 0000   02 50 23 D2 BE 00 00 01 CB 13 00    .P#........
Message Flags = CB = 1100 1011
b1 = broadcast
b2 = group
b3 = ack
b4 = extended
b56 = hops left
b78 = max hops
[2013/10/07 20:37:40] [DEBUG] [InsteonPLM] Running status request:False:True:True:..........
[2013/10/07 20:37:40] [DEBUG] [InsteonPLM] Command: 23.D2.BE 19 00
[2013/10/07 20:37:42] [DEBUG] [InsteonPLM] Transmit>026223d2be0f1900
[2013/10/07 20:37:42] [DEBUG] [InsteonPLM] Receive< 0000   02 50 23 D2 BE 22 FF 5B 41 13 01    .P#..".[A..
1079120c278d439fdc0c998fe6af970e

[2013/10/07 20:37:42] [DEBUG] [InsteonPLM] ValidResponseCheck: 0000   53 44 31 39                SD19
[2013/10/07 20:37:42] [DEBUG] [InsteonPLM] Setting status for:23.D2.BE:19:1..........
[2013/10/07 20:37:42] [DEBUG] [InsteonPLM] Received Command:23.D2.BE:off

        """
        self._result = None
        self.insteon.onCommand(self._insteon_receive_status_callback, '23.D2.BE')
        self.ms.put_read_data(Conversions.hex_to_ascii('025023D2BE000001CB1300'))
        time.sleep(1)
        # Transmits: 026223d2be0f1900
        self.assertEqual(self._result, Command.OFF)

    def test_door_light_delgate_caseinsensitive(self):
        d = Door(address='23.d2.bE', 
                 devices=self.insteon)
        d.close()
        self.ms.put_read_data(Conversions.hex_to_ascii('025023D2BE000001CB1100'))
        time.sleep(3)
        self.ms.put_read_data(Conversions.hex_to_ascii('025023D2BE22FF5B411101'))
        time.sleep(3)
        self.assertEqual(d.state, State.OPEN)

if __name__ == '__main__':
    main()
