from unittest import TestCase, main

from pytomation.common import PytoLogging

class LoggingTests(TestCase):
    def test_log(self):
        logger = PytoLogging(__name__)
        logger.debug('This is a debug statement')
        logger.info('This is an info statement')
        logger.warning('This is a warning statement')
        logger.error('This is an error statement')
        logger.critical('This is a critical statement')
        self.assertTrue(True)