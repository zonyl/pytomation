"""
File:
        upb.py

Description:


Author(s):
         Jason Sharpee <jason@sharpee.com>  http://www.sharpee.com

License:
    This free software is licensed under the terms of the GNU public license, Version 1

Usage:

    see /example_use.py

Example:
    see /example_use.py

Notes:
    To Program devices initially from factory please use PCS UpStart software:
    http://pulseworx.com/Downloads_.htm


    UPB Serial Interface
    http://pulseworx.com/downloads/Interface/PimComm1.6.pdf
    UPB General Protocol
    http://pulseworx.com/downloads/upb/UPBDescriptionv1.4.pdf


Created on May , 2012
"""
import threading
import time
from Queue import Queue
from binascii import unhexlify

from .common import *
from .ha_interface import HAInterface
from ..config import *

class UPBMessage(object):
    class LinkType(object):
        direct = 0
        link = 1

    class RepeatType(object):
        none = 0
        low = 1
        med = 2
        high = 3

    class AckRequestFlag(object):
        ack = 0b001
        ackid = 0b010
        msg = 0b100

    class XmitCount(object):
        one = 0
        two = 1
        three = 2
        four = 3

    class MessageIDSet(object):
        upb_core = 0
        device = 1

    class MessageUPBControl(object):
        retransmit = 0x0d

    class MessageDeviceControl(object):
        activate = 0x20
        deactivate = 0x21
        goto = 0x22

    link_type = LinkType.direct
    repeat_request = RepeatType.none
    packet_length = 0
    ack_request = AckRequestFlag.ack  # | AckRequestFlag.ackid | AckRequestFlag.msg
    xmit_count = XmitCount.one
    xmit_seq = XmitCount.one
    network = 49
    destination = 0
    source = 30
    message_id = MessageIDSet.device
    message_eid = 0
    message_data = None
    checksum = None

    def to_hex(self):
        self.packet_length = 7
        if self.message_data:
            self.packet_length = self.packet_length + len(self.message_data)

        control1 = ((self.link_type & 0b00000011) << 5) | \
                ((self.repeat_request & 0b00000011) << 3) | \
                (self.packet_length & 0b00011111)
        control2 = ((self.ack_request & 0b00000111) << 4) | \
                ((self.xmit_count & 0b00000011) << 2) | \
                (self.xmit_seq & 0b00000011)
        message_command = ((self.message_id & 0b00000111) << 5) | \
                            (self.message_eid & 0b00011111)
        response = Conversions.int_to_hex(control1) + \
                    Conversions.int_to_hex(control2) + \
                    Conversions.int_to_hex(self.network) + \
                    Conversions.int_to_hex(self.destination) + \
                    Conversions.int_to_hex(self.source) + \
                    Conversions.int_to_hex(message_command)
        if self.message_data != None:
            response = response + Conversions.ascii_to_hex(self.message_data)
        response = response + Conversions.int_to_hex(
                                        Conversions.checksum(
                                        Conversions.hex_to_ascii(response)
                                        )
                                     )
        return response


class UPB(HAInterface):
#    MODEM_PREFIX = '\x12'
    MODEM_PREFIX = ''

    def __init__(self, interface):
        super(UPB, self).__init__(interface)
        debug['UPB'] = 0
        
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
            if debug['UPB'] > 0:
                print "[UPB] Response>\n" + hex_dump(responses)
            for response in responses.splitlines():
                responseCode = response[:2]
                if responseCode == 'PA':  # UPB Packet was received by PIM. No ack yet
                    #pass
                    self._processUBP(response, lastPacketHash)
                elif responseCode == 'PU':  # UPB Unsolicited packet received
                    self._processNewUBP(response)
                elif responseCode == 'PK':  # UPB Packet was acknowledged
                    pass
#                    self._processUBP(response, lastPacketHash)
                elif responseCode == 'PR':  # Register read response
                    self._processRegister(response, lastPacketHash)
        else:
            #print "Sleeping"
            #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
            #time.sleep(0.1)
            time.sleep(0.5)

    def _processUBP(self, response, lastPacketHash):
        foundCommandHash = None

        #find our pending command in the list so we can say that we're done (if we are running in syncronous mode - if not well then the caller didn't care)
        for (commandHash, commandDetails) in self._pendingCommandDetails.items():
            if commandDetails['modemCommand'] == self._modemCommands['send_upb']:
                #Looks like this is our command.  Lets deal with it
                self._commandReturnData[commandHash] = True

                waitEvent = commandDetails['waitEvent']
                waitEvent.set()

                foundCommandHash = commandHash
                break

        if foundCommandHash:
            del self._pendingCommandDetails[foundCommandHash]
        else:
            print "[UPB] Unable to find pending command details for the following packet:"
            print hex_dump(response, len(response))

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
            print "[UPB] Unable to find pending command details for the following packet:"
            print hex_dump(response, len(response))

    def _processNewUBP(self, response):
        pass

    def _device_goto(self, address, level, timeout=None, rate=None):
        message = UPBMessage()
        message.network = address[0]
        message.destination = address[1]
        message.message_eid = UPBMessage.MessageDeviceControl.goto
        message.message_data = Conversions.int_to_ascii(level)
        if rate != None:
            message.message_data = message.message_data + \
                                    Conversions.int_to_ascii(rate)
        command = message.to_hex()
        command = command + Conversions.hex_to_ascii('0D')
        commandExecutionDetails = self._sendModemCommand(
                             self._modemCommands['send_upb'], command)
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    def on(self, address, timeout=None, rate=None):
        return self._device_goto(address, 0x64, timeout=timeout)

    def off(self, address, timeout=None, rate=None):
        return self._device_goto(address, 0x00, timeout=timeout)
