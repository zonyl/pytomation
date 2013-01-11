from unittest import TestCase

from pytomation.interfaces import Command
from pytomation.devices import Attributes, State2

class AttributesTest(TestCase):
    def test_instance(self):
        a = Attributes()
        self.assertIsNotNone(a)

    def test_attriubte(self):
        a = Attributes(
                       command=Command.OFF
                       )
        self.assertEqual(a.command, Command.OFF)
        