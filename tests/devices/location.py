from datetime import datetime

from unittest import TestCase, main
from mock import Mock, patch

from pytomation.devices import Location, State, Light


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
        
    def test_civil(self):
        ph_standard = Location('35.2269', '-80.8433', 
                       tz='US/Eastern', 
                       mode=Location.MODE.CIVIL, 
                       is_dst=True,
                       local_time=datetime(2012,11,26,17,15,0))
        self.assertIsNotNone(ph_standard)
        
    def test_delegate(self):
        self.loc.local_time = datetime(2012,6,1,1,0,0)
        self.assertEqual(self.loc.state, State.DARK)
        l = Light(devices=self.loc)
        self.assertEqual(l.state, State.ON)
        self.assertEqual(self.loc.state, State.DARK)

        self.loc.local_time = datetime(2012,6,1,12,0,0)
        self.assertEqual(self.loc.state, State.LIGHT)
        self.assertEqual(l.state, State.OFF)