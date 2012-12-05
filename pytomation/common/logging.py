from __future__ import absolute_import
import logging
from .config import *


class Logging(object):
    
    def __init__(self, *args, **kwargs):
        self._name = args[0]
        self._log_file = logging_file
        default_log_file = 'pytomation.log'
        if not self._log_file:
            self._log_file = default_log_file
        try:
            self._basic_config(self._log_file)
        except:
            self._basic_config(default_log_file)
            
        self._logger = logging.getLogger(self._name)
        
        #get module specifics
        module_level_name = logging_modules.get(self._name, logging_default_level)
        if module_level_name:
            module_level = getattr(logging, module_level_name)
            self._logger.setLevel(module_level)


    def _basic_config(self, filename):
        log_level = getattr(logging, logging_default_level)
        logging.basicConfig(
                            filename=filename,
                            format=logging_format,
                            datefmt=logging_datefmt,
                            level=log_level,
                            )
        
    def __getattr__(self, name):
        return getattr(self._logger, name)