import Queue
from pytomation.interfaces import Conversions
from pytomation.interfaces.common import *

class Mock_Interface(object):
    def __init__(self, *args, **kwargs):
        super(Mock_Interface, self).__init__(*args, **kwargs)
        self._read_data = ""
        self._write_data = []
        
    def read(self, count=None):
        print 'Reading for {0} bytes'.format(count)
        if count:
            data = self._read_data[:count]
            self._read_data = self._read_data[count:]
        else:
            data = self._read_data
            self._read_data = ""
            
        print 'Returning data hhhh:' + hex_dump(data) + ":"
        return data

    def write(self, data=None, **kwargs):
        #print 'kkkkk' + str(kwargs)
        self._write_data.append(data)
        return True
    
    def put_read_data(self, data):
        print 'Adding data: ' + hex_dump(data) + ":"
        self._read_data += data
    
    def query_write_data(self):
        return self._write_data

    def clear_write_data(self):
        self._write_data = []