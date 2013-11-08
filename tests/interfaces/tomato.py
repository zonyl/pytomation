import time

from unittest import TestCase

from tests.common import MockInterface, Mock_Interface
from pytomation.interfaces import HTTP, TomatoInterface, HTTP

class TomatoInterfaceTests(TestCase):
    def setUp(self):
        self.host = '192.168.13.1'
#        self.i = HTTP('http', self.host, username='root', password='password')
        self.i = Mock_Interface()
        self.interface = TomatoInterface(self.i, self.host, http_id='asdfaadsfasdf234')

    def test_instantiation(self):
        self.assertIsInstance(self.interface, TomatoInterface)

    def test_restriction(self):
        """
        _nextpage:restrict.asp
_service:restrict-restart
rrule1:1|-1|-1|127|192.168.13.119>192.168.13.202|||0|Roku
f_enabled:on
f_desc:Roku
f_sched_allday:on
f_sched_everyday:on
f_sched_begin:0
f_sched_end:0
f_sched_sun:on
f_sched_mon:on
f_sched_tue:on
f_sched_wed:on
f_sched_thu:on
f_sched_fri:on
f_sched_sat:on
f_type:on
f_comp_all:1
f_block_all:on
f_block_http:
_http_id:
"""
        self.interface.restriction('Roku', True)
        
        time.sleep(2)
        #data = self.i.query_write_data()
        #self.assertIn(("f_desc", "Roku"), data[0].items())
        self.i.clear_write_data()
        
