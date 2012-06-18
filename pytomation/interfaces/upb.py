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

from .common import HAInterface, Conversions

class UPB(HAInterface):
    def __init__(self, interface=None, *args, **kwargs):
        self.__interface = interface
        self.__write_queue = Queue()
        self.__interfaceRunningEvent = threading.Event()
        self.__shutdownEvent = threading.Event()
        super(UPB, self).__init__()
        
    
    def command_interface(self, data):
        self.__write_queue.put(data)

    def get_registers(self):
        prefix = Conversions.hex_to_ascii('12')
        command = Conversions.hex_to_ascii('00FF')
        print Conversions.hex_dump(command)
        command = command + Conversions.int_to_ascii(Conversions.checksum(command))
        print Conversions.hex_dump(command)
        command = prefix + command + Conversions.hex_to_ascii('0D')
        print Conversions.hex_dump(command)
        command = Conversions.hex_to_ascii('120080800D')
        self.command_interface(command)

    def shutdown(self):
        if self.__interfaceRunningEvent.isSet():
            self.__shutdownEvent.set()

            #wait 2 seconds for the interface to shut down
            self.__interfaceRunningEvent.wait(2000)
            
    def run(self):
        self.__interfaceRunningEvent.set();
        while not self.__shutdownEvent.isSet():
            # Process received data first
            read_command = self.__interface.read()
            if read_command:
                print ">:" + read_command + ":" + Conversions.hex_dump(read_command)
            # Write outgoing traffic
            
            if not self.__write_queue.empty():
                write_command = self.__write_queue.get_nowait()
                self.__interface.write(write_command)
                print "<:" + write_command + ":" + Conversions.hex_dump(write_command)
            time.sleep(0.5)