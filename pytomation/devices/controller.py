'''
File:
    controller.py

Description:
    A helper class for defining an address for a scene controller

Author(s): 
    Chris Van Orman

License:
    This free software is licensed under the terms of the GNU public license, Version 1     

Usage:


Example: 

Notes:


Created on Mar 11, 2013
'''
class Controller(object):
    def __init__(self, device=None, group=1, address=None):
        self._address = device.address if device else None
        if (self._address and group):
            self._address += ':%02X' % group
        self._address = address if address else self._address

    def addressMatches(self, address):
        return self._address == address
