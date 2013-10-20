import time

from datetime import datetime

from unittest import TestCase, main
from mock import Mock, patch

from pytomation.devices import Location, State, Light, Command, Attribute


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
        
    def test_read_only(self):
        self.loc.local_time = datetime(2012,6,1,0,0,0)
        self.assertEqual(self.loc.state, State.DARK)
        l2 = Light()
        l = Light(devices=(self.loc, l2))
        self.assertEqual(self.loc.state, State.DARK)
        l.on()
        self.assertEqual(l.state, State.ON)
        self.assertEqual(self.loc.state, State.DARK)
        l.off()
        self.assertEqual(self.loc.state, State.DARK)
        l2.off()
        self.assertEqual(self.loc.state, State.DARK)
        l2.on()
        self.assertEqual(self.loc.state, State.DARK)

    def test_gc_1(self):
        twilight_standard = Location( '42.2671389', '-71.8756111', 
                               tz='US/Eastern', 
                               mode=Location.MODE.STANDARD, 
                               is_dst=True,
                               name='Standard Twilight')
        
        twilight_standard.local_time = datetime(2012,6,1,0,0,0)
        self.assertEqual(twilight_standard.state, State.DARK)

        _back_porch = Light(address='21.03.24',
              devices=(twilight_standard),
              initial=twilight_standard,
#              command=(   {  Attribute.COMMAND: (Command.DARK),   Attribute.MAPPED: (Command.ON),   Attribute.SOURCE: (twilight_standard),  },
#                                   { Attribute.COMMAND: (Command.LIGHT),  Attribute.MAPPED: (Command.OFF),  Attribute.SOURCE: (twilight_standard), }, ),
              map=(   {  Attribute.COMMAND: (Command.DARK),   Attribute.MAPPED: (Command.ON),   Attribute.SOURCE: (twilight_standard),  },
                                   { Attribute.COMMAND: (Command.LIGHT),  Attribute.MAPPED: (Command.OFF),  Attribute.SOURCE: (twilight_standard), }, ),

              ignore=(  {   Attribute.COMMAND: Command.OFF,   Attribute.SOURCE: twilight_standard, }, ),
              time=(  { Attribute.COMMAND:(Command.LEVEL, 30),  Attribute.TIME: '11:15pm',    }, ),
              name="Back porch light")
        
        self.assertEqual(twilight_standard.state, State.DARK)
        self.assertEqual(_back_porch.state, State.ON)
        
        
