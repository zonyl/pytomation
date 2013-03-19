import os, tempfile, time
import RPi.GPIO as GPIO

from .common import Interface
from ..common.pytomation_object import PytoLogging

class RPIInput(Interface):
    def __init__(self, pin):
        super(RPIInput, self).__init__()
        self._pin = pin
	self._state = "unknown"
        self._logger = PytoLogging(self.__class__.__name__)
	GPIO.setup(pin, GPIO.IN)

    def read(self, bufferSize=1024):
	result = "open"

	input_value = GPIO.input(self._pin)

	if (input_value == 1):
		result = "close"

	#return result only if it is different than the last read.
	if (result != self._state):
		self._state = result
	else:
		result = ""

	return result

    def write(self, bytesToSend):
        return None

    def close(self):
	pass
