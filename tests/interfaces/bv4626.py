import select
import time

from unittest import TestCase, main
from mock import Mock
from tests.common import MockInterface
from pytomation.interfaces import Bv4626, Serial, HACommand
from pytomation.devices import State

class Bv4626Tests(TestCase):
    useMock = True

    def setUp(self):
        self.ms = MockInterface()

        self.serial = None
        if not self.useMock:  # Use Mock Serial Port
            self.serial = Serial('/dev/ttyUSB0', 115200, rtscts=True)

        self.byvac = Bv4626(self.ms if self.useMock else self.serial, outputs='abefh', sockets='c')

        self.ms.add_response({'\015': '*'})
        self.ms.add_response({'\033[72s': self.byvac.ACK})

    def tearDown(self):
        self.byvac.shutdown()
        self.serial = None

    def test_a_instantiation(self):
        self.assertIsNotNone(self.byvac,
                             'BV4626 interface could not be instantiated')

    def test_b_outputs(self):
        self.ms.add_response({'\033[' + self.byvac._modemCommands['turnOn'] + 'A': self.byvac.ACK})
        self.ms.add_response({'\033[' + self.byvac._modemCommands['turnOff'] + 'A': self.byvac.ACK})
        self.ms.add_response({'\033[' + self.byvac._modemCommands['turnOn'] + 'B': self.byvac.ACK})
        self.ms.add_response({'\033[' + self.byvac._modemCommands['turnOff'] + 'B': self.byvac.ACK})
        self.ms.add_response({'\033[255a': self.byvac.ACK})
        self.ms.add_response({'\033[0a': self.byvac.ACK})
        self.ms.add_response({'\033[255h': self.byvac.ACK})
        self.ms.add_response({'\033[0h': self.byvac.ACK})

        # Relay outputs
        response = self.byvac.on('A')
        self.assertTrue(response)
        self.serial and time.sleep(0.25)
        response = self.byvac.on('B')
        self.assertTrue(response)
        self.serial and time.sleep(0.5)
        response = self.byvac.off('A')
        self.assertTrue(response)
        self.serial and time.sleep(0.25)
        response = self.byvac.off('B')
        self.assertTrue(response)

        response = self.byvac.on('C')
        self.assertFalse(response)


        # I/O or Switch Outputs
        response = self.byvac.on('a')
        self.assertTrue(response)
        self.serial and time.sleep(0.25)
        response = self.byvac.on('h')
        self.assertTrue(response)
        self.serial and time.sleep(0.5)
        response = self.byvac.off('a')
        self.assertTrue(response)
        self.serial and time.sleep(0.25)
        response = self.byvac.off('h')
        self.assertTrue(response)

        response = self.byvac.on('c')
        self.assertFalse(response)


        # I/O mapped Maplin Wireless Sockets
        response = self.byvac.on('a44')
        self.assertFalse(response)

        response = self.byvac.on('c11')
        self.assertTrue(response)
        self.serial and time.sleep(0.5)
        response = self.byvac.off('c11')
        self.assertTrue(response)


    def test_c_get_device_id(self):
        # What will be written / what should we get back
        self.ms.add_response({'\033['+self.byvac._modemCommands['getDeviceId']: '4626'+self.byvac.ACK})

        response = self.byvac.getDeviceId()
        self.assertEqual(response, '4626')

    def test_d_get_firmware_version(self):
        # What will be written / what should we get back
        self.ms.add_response({'\033['+self.byvac._modemCommands['getFirmwareVersion']: '12'+self.byvac.ACK})

        response = self.byvac.getFirmwareVersion()
        self.assertEqual(response, '12')


if __name__ == '__main__':
    main()
