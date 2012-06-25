import select

from unittest import TestCase, main

from pytomation.interfaces import UPB, Serial, HACommand


class UPBInterfaceTests(TestCase):

    def setUp(self):
        self.serial = Serial('/dev/ttyUSB0', 4800)
        self.upb = UPB(self.serial)
        self.upb.start()

    def test_instantiation(self):
        self.assertIsNotNone(self.upb,
                             'UPB interface could not be instantiated')

    def test_get_firmware_version(self):
        useMock = True
        if useMock:  # Use Mock Serial Port
            ms = MockSerial()
            ms._response = 'PR021234\x0D'
            self.upb = None
            self.upb = UPB(ms)
            self.upb.start()

        response = self.upb.get_register(2, 2)
        self.assertEqual(response, '1234')
        if useMock:
            self.assertEqual(ms._written, '\x120202FC\x0D')
        #sit and spin, let the magic happen
        #select.select([], [], [])


class MockSerial(object):
    _written = None
    _response = None
    _response_q = None

    def __init__(self, *args, **kwargs):
        pass

    def write(self, data=None):
        self._written = data
        self._response_q = self._response

    def read(self, count=None):
        response = ""
        if self._response_q:
            if not count:
                count = len(self._response_q)
                response = self._response_q[:count]
                self._response_q = None
        return response

if __name__ == '__main__':
    main()
