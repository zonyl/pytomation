from datetime import datetime

from unittest import TestCase, main
from mock import Mock, patch

from pytomation.devices import Location, State


class LocationTests(TestCase):
    def setUp(self):
        self.loc = Location('35.2269', '-80.8433')

    def test_sunset(self):
        self.loc.local_time = datetime(2012,6,1,0,0,0)
#        MockDateTime.now = classmethod(lambda x: datetime(2012,6,1,0,0,0))
        self.assertEqual(self.loc.state, State.DARK)
#        MockDateTime.now = classmethod(lambda x: datetime(2012,6,1,12,0,0))
        self.loc.local_time = datetime(2012,6,1,12,0,0)
        self.assertEqual(self.loc.state, State.LIGHT)
        