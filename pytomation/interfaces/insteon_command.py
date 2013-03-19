'''
File:
    insteon_command.py

Description:
    A set of classes supporting Insteon communication

Author(s): 
    Chris Van Orman

License:
    This free software is licensed under the terms of the GNU public license, Version 1     

Usage:

Example: 

Notes:

Created on Mar 11, 2013
'''
class InsteonCommand(object):
    def __init__(self, data, *args, **kwargs):
        self._data = data
        
    def setAddress(self,data):
        pass
        
    def setFlags(self, data):
        pass
    
    def setSecondary(self,data):
        pass 

    def getBytes(self):
        return str(bytearray(self._data))
    
class InsteonStandardCommand(InsteonCommand):
    def __init__(self, data, *args, **kwargs):
        super(InsteonStandardCommand, self).__init__(data, *args, **kwargs)
        self._data = [0x62,0,0,0,0x0F] + self._data
        self._minAckLength = 10
        self._ackCommand = 0x50

    def _getAddress(self, data):
        return data[1:4]
        
    def setAddress(self,data):
        self._data[1:4] = data
        
    def setFlags(self, data):
        self._data[4] = data
        
    def setSecondary(self,data):
        self._data[6:] = data

    def isAck(self, data):
        #basically we are just checking that the message is the right length,
        #has the correct address and the command number is correct
        return len(data) >= self._minAckLength and \
            data[0] == self._ackCommand and \
            self._getAddress(data) == self._getAddress(self._data)

class InsteonExtendedCommand(InsteonStandardCommand):
    def __init__(self, data, *args, **kwargs):
        super(InsteonExtendedCommand, self).__init__(data, *args, **kwargs)
        self._data = self._data + [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #The extended response is 0x51, but the actual ACK from the device is still 0x50.
        self._ackCommand = 0x50
        self.setFlags(0x1F)
    
class InsteonAllLinkCommand(InsteonStandardCommand):
    def __init__(self, data, *args, **kwargs):
        super(InsteonAllLinkCommand, self).__init__(data, *args, **kwargs)
        self._data = [0x61,0] + data
        self._ackCommand = 0x61
        self._minAckLength = 4

    def _getAddress(self, data):
        return data[1]
        
    def setAddress(self,data):
        self._data[1] = data[2] if len(data) == 3 else data
        
    def setFlags(self, data):
        pass
        
    def setSecondary(self,data):
        self._data[3] = data
        
