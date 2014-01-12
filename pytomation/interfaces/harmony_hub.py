import time

from interruptingcow import timeout

from harmony.client import HarmonyClient
from harmony.auth import login
from .ha_interface import HAInterface
from .common import *


"""
Harmony Interface 

"""

class HarmonyHub(HAInterface):
    def __init__(self, address=None, port=5222, user=None, password=None, *args, **kwargs):
        self._ip = address
        self._port = port
        self._user = user
        self._password = password
        
        self._create_connection()
        
        super(HarmonyHub, self).__init__(None, *args, **kwargs)

    def _create_connection(self):
        try:
            with timeout(15, exception=RuntimeError):
                self._token = login(self._user, self._password)
                self._conn = HarmonyClient(self._token)
                print "he" +str(self._ip) + ":"  + str(self._port)
                self._conn.connect(address=(self._ip, self._port),
                           use_tls=False, use_ssl=False)
                print 'adf'
                self._conn.process(block=False)
        
                while not self._conn.sessionstarted:
                    time.sleep(0.1)

        except RuntimeError:
            self._logger.error("Harmony: Connection error")
            raise RuntimeError
            return False
        return True

    def on(self, *args, **kwargs):
        print str(args, **kwargs)
#        self._conn.start_activity('7174686')
        self._conn.start_activity(args[0])
        
    def off(self, *args, **kwargs):
        self._conn.start_activity(-1)
        
    def get_config(self):
        return self._conn.get_config()
        