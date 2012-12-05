from unittest import TestCase, main

from pytomation.common import Logging

class LoggingTests(TestCase):
    def test_log(self):
        logger = Logging(__name__)
        logger.debug('This is a debug statement')
        logger.info('This is an info statement')
        logger.warning('This is a warning statement')
        logger.error('This is an error statement')
        logger.critical('This is a critical statement')
        self.assertTrue(True)