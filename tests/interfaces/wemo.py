import time

from unittest import TestCase

from tests.common import MockInterface
from pytomation.interfaces import WeMo

class WeMoTests(TestCase):
    def setUp(self):
        self.host = '192.168.13.210'
        self.i = MockInterface()
        self.interface = WeMo(self.i, self.host)

    def test_instantiation(self):
        self.assertIsInstance(self.interface, WeMo)