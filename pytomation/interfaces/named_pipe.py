import os, tempfile, time

from .common import Interface
from ..common.pytomation_object import PytoLogging

class NamedPipe(Interface):
    def __init__(self, path_name, is_read=True):
        super(NamedPipe, self).__init__()
        self._path_name = path_name
        self._is_read = is_read
        self._logger = PytoLogging(self.__class__.__name__)
        self._create_named_pipe(path_name)

    def _create_named_pipe(self, path_name):
        try:
            os.mkfifo(path_name)
        except OSError, ex:
            self._logger.warning("Failed to create FIFO: %s" % ex)
        except Exception, ex:
            self._logger.critical("Unknown exception: %s" % ex)
            return
        if self._is_read:
# Unintuitive behavior IMO: 
#   http://stackoverflow.com/questions/5782279/python-why-does-a-read-only-open-of-a-named-pipe-block
#            self._pipe = open(path_name, 'r')
            self._pipe = os.open(path_name, os.O_RDONLY|os.O_NONBLOCK)
        else:
#            self._pipe = open(path_name, 'w')
            self._pipe = os.open(path_name, os.O_WRONLY|os.O_NONBLOCK)
            
    def read(self, bufferSize=1024):
        result = ''
        try:
            result = os.read(self._pipe, bufferSize)
        except OSError, ex:
            self._logger.debug('Nothing to read in pipe: %s' % ex)
        except Exception, ex:
            self._logger.error('Error reading pipe %s' % ex)
            raise ex
        return result.strip()

    def write(self, bytesToSend):
        return os.write(self._pipe, bytesToSend)

    def close(self):
#        self._pipe.close()
        os.close(self._pipe)
        os.remove(self._path_name)
#        os.rmdir(tmpdir)    
