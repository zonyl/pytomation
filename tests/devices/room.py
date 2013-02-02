from unittest import TestCase

from pytomation.devices import Room

class RoomTests(TestCase):
    def setUp(self):
        pass
    
    def test_init(self):
        r = Room()
        self.assertIsNotNone(r)