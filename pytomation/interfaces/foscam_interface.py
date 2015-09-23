from .ha_interface import HAInterface
from pytomation.devices import State
from .common import Command
from foscam import FoscamCamera
import time


class Foscam(HAInterface):
    MOTIONDETECTION_OFF = '0'
    MOTIONDETECTION_ON = '1'
    MOTIONDETECTION_ALERT = '2'

    _iteration = 0
    _poll_secs = 15

    def __init__(self, *args, **kwargs):
        super(Foscam, self).__init__(None, *args, **kwargs)

    def _init(self, *args, **kwargs):
        super(Foscam, self)._init(*args, **kwargs)
        self._host = kwargs.get('host', None)
        self._port = kwargs.get('port', None)
        self._username = kwargs.get('username', None)
        self._password = kwargs.get('password', None)
        self._interface = FoscamCamera(host=self._host, port=self._port, usr=self._username, pwd=self._password, verbose=False)

    def _readInterface(self, lastPacketHash):
	if not self._iteration < self._poll_secs:
		self._iteration = 0
		motion = self._interface.get_dev_state()[1]['motionDetectAlarm'][0]

		if motion == self.MOTIONDETECTION_ALERT:
		    self._onCommand(command=Command.MOTION, address=self._host)

		if motion == self.MOTIONDETECTION_ON:
		    self._onCommand(command=(Command.STILL))

		if motion == self.MOTIONDETECTION_OFF:
		    self._onCommand(command=(Command.OFF))
	self._iteration += 1
        time.sleep(1)

    def activate(self, *args, **kwargs):
        self._interface.enable_motion_detection()

    def deactivate(self, *args, **kwargs):
        self._interface.disable_motion_detection()
