from datetime import datetime

from unittest import TestCase, main
from mock import Mock, patch

from pytomation.devices import Location2, State2, Light2


class Location2Tests(TestCase):
    def setUp(self):
        self.loc = Location2('35.2269', '-80.8433')

    def test_sunset(self):
        self.loc.local_time = datetime(2012,6,1,0,0,0)
#        MockDateTime.now = classmethod(lambda x: datetime(2012,6,1,0,0,0))
        self.assertEqual(self.loc.state, State2.DARK)
#        MockDateTime.now = classmethod(lambda x: datetime(2012,6,1,12,0,0))
        self.loc.local_time = datetime(2012,6,1,12,0,0)
        self.assertEqual(self.loc.state, State2.LIGHT)
        
    def test_civil(self):
        ph_standard = Location2('35.2269', '-80.8433', 
                       tz='US/Eastern', 
                       mode=Location2.MODE.CIVIL, 
                       is_dst=True,
                       local_time=datetime(2012,11,26,17,15,0))
        self.assertIsNotNone(ph_standard)
        
    def test_delegate(self):
        self.loc = Location2('35.2269', '-80.8433')
        l = Light2(devices=self.loc)
        self.assertEqual(l.state, State2.ON)
        self.loc.local_time = datetime(2012,6,1,0,0,0)
#        MockDateTime.now = classmethod(lambda x: datetime(2012,6,1,0,0,0))
        self.assertEqual(self.loc.state, State2.DARK)
        self.assertEqual(l.state, State2.ON)
#        MockDateTime.now = classmethod(lambda x: datetime(2012,6,1,12,0,0))
        self.loc.local_time = datetime(2012,6,1,12,0,0)
        self.assertEqual(self.loc.state, State2.LIGHT)
        self.assertEqual(l.state, State2.OFF)