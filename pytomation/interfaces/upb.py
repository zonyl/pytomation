"""
UPB Serial Interface
http://pulseworx.com/downloads/Interface/PimComm1.6.pdf
UPB General Protocol
http://pulseworx.com/downloads/upb/UPBDescriptionv1.4.pdf
"""
import threading
import time
from Queue import Queue
from binascii import unhexlify

from .common import Conversions
from .ha_interface import HAInterface


class UPB(HAInterface):
#    MODEM_PREFIX = '\x12'
    MODEM_PREFIX = ''
    
    def __init__(self, interface=None, *args, **kwargs):
        super(UPB, self).__init__(interface)
        self._write_queue = Queue()
        
    
    def command_interface(self, data):
        command = {'command': data,
                   'lock': threading.Lock() }
        self._write_queue.put(data)
        

    def get_registers(self):
        prefix = Conversions.hex_to_ascii('12')
        command = '00FF'
        command = command + Conversions.int_to_hex(Conversions.checksum(Conversions.hex_to_ascii(command)))
        command = prefix + command + Conversions.hex_to_ascii('0D')
#        command = Conversions.hex_to_ascii('120080800D')
#        command = Conversions.hex_to_ascii('1200FF010D')
#        self.command_interface(command)
        self._sendModemCommand(command)

    def runer(self):
        self._interfaceRunningEvent.set();
        while not self._shutdownEvent.isSet():
            # Process received data first
            read_command = self._interface.read()
            if read_command:
                print ">:" + read_command + ":" + Conversions.hex_dump(read_command)
            # Write outgoing traffic
            
            if not self._write_queue.empty():
                write_command = self._write_queue.get_nowait()
                count = self._interface.write(write_command)
                print "<:" + write_command + ":" + str(count) + ":" + Conversions.hex_dump(write_command)
            time.sleep(0.5)