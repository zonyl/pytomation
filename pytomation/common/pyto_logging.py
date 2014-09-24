import logging
from logging.handlers import TimedRotatingFileHandler

from ..common import config


class PytoLogging(object):
    """
    Provides pytomation specific logging.
    """
    loaded_handlers = []

    def __init__(self, *args, **kwargs):
        self._name = args[0]
        self._log_file = config.logging_file
        default_log_file = 'pytomation.log'
        if not self._log_file:
            self._log_file = default_log_file
            
        self._logger = logging.getLogger(self._name)
        module_level_name = config.logging_modules.get(self._name, config.logging_default_level)
        if config.logging_rotate_when:
            try:
                th = TimedRotatingFileHandler(filename=config.logging_file,
                                                                 when=config.logging_rotate_when,
                                                                 interval=config.logging_rotate_interval,
                                                                 backupCount=config.logging_rotate_backup )
            except Exception, ex:
                th = TimedRotatingFileHandler(filename=default_log_file,
                                                                 when=config.logging_rotate_when,
                                                                 interval=config.logging_rotate_interval,
                                                                 backupCount=config.logging_rotate_backup )
                
            if module_level_name:
                module_level = getattr(logging, module_level_name)
#                th.setLevel(module_level)
            th.setFormatter(logging.Formatter(fmt=config.logging_format, datefmt=config.logging_datefmt))
            if not self._name in self.loaded_handlers:
            	self._logger.addHandler(th)
		self.loaded_handlers.append(self._name)
        else:
            try:
                self._basic_config(self._log_file)
            except:
                self._basic_config(default_log_file)
        #get module specifics
        if module_level_name:
            module_level = getattr(logging, module_level_name)
            self._logger.setLevel(module_level)


    def _basic_config(self, filename):
        log_level = getattr(logging, config.logging_default_level)
        logging.basicConfig(
                            filename=filename,
                            format=config.logging_format,
                            datefmt=config.logging_datefmt,
                            level=log_level,
                            )
        
    def __getattr__(self, name):
        return getattr(self._logger, name)
