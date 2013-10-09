import time

from unittest import TestCase

from tests.common import MockInterface, Mock_Interface
from pytomation.interfaces import HTTP, SparkIO

class SparkIOTests(TestCase):
    def setUp(self):
        self.host = 'api.sprk.io'
        self.i = HTTP('https', self.host)
#        self.i = Mock_Interface()
        self.interface = SparkIO(self.i, self.host)

    def test_instantiation(self):
        self.assertIsInstance(self.interface, SparkIO)

    def test_on(self):
        # Address = (:id, pin)
        result = self.interface.on(('elroy', 'D0'))
        self.assertEqual(result, True)
        time.sleep(5)
        
"""
## Initially this was working
jason@x120:~/projects/pytomation$ curl https://api.sprk.io/v1/devices/elroy -d pin=D0 -d level=HIGH
{
  "ok": true
}
## However, now the API is giving me an auth error now!  Not sure what is going on over there
jason@x120:~/projects/pytomation$ curl https://api.sprk.io/v1/devices/elroy -d pin=D0 -d level=HIGH
{
  "code": 400,
  "error": "invalid_request",
  "error_description": "The access token was not found"
}
"""
        #         
#     def test_circulate(self):
#         self.interface.off(self.host)
#         time.sleep(2)
#         self.interface.circulate(self.host)
#     
#     def test_setpoint(self):
#         #no prior mode, then default to heat
#         self.interface.level(address=self.host, level=72)
#         time.sleep(2)
#         self.assertIn(('tstat', '{"t_heat": 72}'), self.i.query_write_data())
#         self.i.clear_write_data()
#         self.interface.cool()
#         time.sleep(2)
#         self.assertIn(('tstat', '{"tmode": 2, "t_cool": 72}'), self.i.query_write_data())
#         
#     def test_cool(self):
#         self.interface.cool()
#         time.sleep(2)
#         self.assertIn(('tstat', '{"tmode": 2}'), self.i.query_write_data())
#         