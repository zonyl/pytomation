from unittest import TestCase, main
from mock import Mock, patch

from pytomation.devices import Location, State


class LocationTests(TestCase):
    def setUp(self):
        self.loc = Location(35.2269, -80.8433)

    @patch('time')    
    def test_sunset(self, mockTime):
        mockTime.now = ''
        self.loc.mode = Location.MODE.STANDARD
        self.assertEqual(self.loc.state, State.DARK)
        
        