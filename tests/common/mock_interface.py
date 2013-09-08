import Queue
from pytomation.interfaces import Conversions
from pytomation.interfaces.common import *

class Mock_Interface(object):
    def __init__(self, *args, **kwargs):
        super(Mock_Interface, self).__init__(*args, **kwargs)
        self.read_data = ""
        
    def read(self, count=None):
        print 'Reading for {0} bytes'.format(count)
        if count:
            data = self.read_data[:count]
            self.read_data = self.read_data[count:]
        else:
            data = self.read_data
            self.read_data = ""
            
        print 'Returning data hhhh:' + hex_dump(data) + ":"
        return data

    def write(self, data=None):
        return True
    
    def put_read_data(self, data):
        print 'Adding data: ' + hex_dump(data) + ":"
        self.read_data += data
    
    