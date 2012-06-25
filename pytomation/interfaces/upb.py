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

from .common import *
from .ha_interface import HAInterface


class UPB(HAInterface):
#    MODEM_PREFIX = '\x12'
    MODEM_PREFIX = ''

    def __init__(self, interface):
        super(UPB, self).__init__(interface)
        self._modemRegisters = ""

        self._modemCommands = {
                               'send_upb': '\x14',
                               'read_register': '\x12',
                               'write_register': 'x17'
                               }

        self._modemResponse = {'PA': 'send_upb',
                               'PK': 'send_upb',
                               'PB': 'send_upb',
                               'PE': 'send_upb',
                               'PN': 'send_upb',
                               'PR': 'read_register',
                               }

    def get_register(self, start=0, end=255, timeout=None):
#        command = Conversions.hex_to_ascii('120080800D')
#        command = Conversions.hex_to_ascii('1200FF010D')
        command = Conversions.int_to_hex(start) + Conversions.int_to_hex(end)
        command = command + Conversions.int_to_hex(
                               Conversions.checksum(
                                    Conversions.hex_to_ascii(command)
                                    )
                               )
        command = command + Conversions.hex_to_ascii('0D')
        commandExecutionDetails = self._sendModemCommand(
                             self._modemCommands['read_register'], command)
        return self._waitForCommandToFinish(commandExecutionDetails,
                                             timeout=timeout)


    def _readModem(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read()
        if len(responses) != 0:
            print "Response>\n" + hex_dump(responses)
            for response in responses.splitlines():
                responseCode = response[:2]
                if responseCode == 'PA':  # UPB Packet was received by PIM. No ack yet
                    self._processUBP(response, lastPacketHash)
                elif responseCode == 'PU':  # UPB Unsolicited packet received
                    self._processNewUBP(response)
                elif responseCode == 'PK':  # UPB Packet was acknowledged
                    self._processUBP(response, lastPacketHash)
                elif responseCode == 'PR':  # Register read response
                    self._processRegister(response, lastPacketHash)
        else:
            #print "Sleeping"
            #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
            #time.sleep(0.1)
            time.sleep(0.5)

    def _processUBP(self, response, lastPacketHash):
        pass

    def _processRegister(self, response, lastPacketHash):
        foundCommandHash = None

        #find our pending command in the list so we can say that we're done (if we are running in syncronous mode - if not well then the caller didn't care)
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
            if commandDetails['modemCommand'] == self._modemCommands['read_register']:
                #Looks like this is our command.  Lets deal with it
                self._commandReturnData[commandHash] = response[4:]

                waitEvent = commandDetails['waitEvent']
                waitEvent.set()

                foundCommandHash = commandHash
                break

        if foundCommandHash:
            del self._pendingCommandDetails[foundCommandHash]
        else:
            print "Unable to find pending command details for the following packet:"
            print hex_dump(response, len(response))

    def _processNewUBP(self, response):
        pass