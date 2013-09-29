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

Versions and changes:
    Initial version created on May, 2012
    2012/11/14 - 1.1 - Added debug levels and global debug system
    2012/11/19 - 1.2 - Added logging, use pylog instead of print
    2012/11/30 - 1.3 - Unify Command and State magic strings across the system

"""
import threading
import time
from Queue import Queue
from binascii import unhexlify

from .common import *
from .ha_interface import HAInterface

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
        upb_report = 4
        extended = 7

    class MessageUPBControl(object):
        retransmit = 0x0d

    class MessageDeviceControl(object):
        activate = 0x20
        deactivate = 0x21
        goto = 0x22
        fade_start = 0x23
        report_state = 0x30
        state_response=0x86
        

    link_type = LinkType.direct
    repeat_request = RepeatType.none
    packet_length = 0
    ack_request = AckRequestFlag.ack  # | AckRequestFlag.ackid | AckRequestFlag.msg
    xmit_count = XmitCount.one
    xmit_seq = XmitCount.one
    network = 49
    destination = 0
    source = 30
#    message_id = MessageIDSet.device
#    message_eid = 0
    message_did = 0
    message_data = None
    checksum = None

    def to_hex(self):
        self.packet_length = 7
        if self.message_data:
            self.packet_length = self.packet_length + len(self.message_data)

#        control1 = ((self.link_type & 0b00000011) << 5) | \
#                ((self.repeat_request & 0b00000011) << 3) | \
#                (self.packet_length & 0b00011111)
        control1 = ((self.link_type & 0b00000001) << 7) | \
                ((self.repeat_request & 0b00000011) << 5) | \
                (self.packet_length & 0b00011111)

        control2 = ((self.ack_request & 0b00000111) << 4) | \
                ((self.xmit_count & 0b00000011) << 2) | \
                (self.xmit_seq & 0b00000011)
#        message_command = ((self.message_id & 0b00000111) << 5) | \
#                            (self.message_eid & 0b00011111)
        message_command = self.message_did
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

    def decode(self, message):
        control1 = Conversions.hex_to_int(message[2:4])
        control2 = Conversions.hex_to_int(message[4:6])
        self.link_type = (control1 & 0b10000000) >> 7
        self.repeat_request = (control1 & 0b01100000) >> 5
        self.packet_length = (control1 & 0b00011111)
        self.ack_request = (control2 & 0b01110000) >> 4
        self.xmit_count = (control2 & 0b00001100) >> 2
        self.xmit_seq = (control2 & 0b00000011)
        
        self.network = Conversions.hex_to_int(message[6:8])
        self.destination = Conversions.hex_to_int(message[8:10])
        self.source = Conversions.hex_to_int(message[10:12])
        
        message_header = Conversions.hex_to_int(message[12:14])
 #       self.message_id = (message_header & 0b11100000) >> 5
 #       self.message_eid = (message_header & 0b00011111)
        self.message_did = message_header
        self.message_data = message[14:]

class UPB(HAInterface):
#    MODEM_PREFIX = '\x12'
    MODEM_PREFIX = ''
    VERSION = '1.4'

    def __init__(self, interface, *args, **kwargs):
        super(UPB, self).__init__(interface, *args, **kwargs)

    def _init(self, *args, **kwargs):
        super(UPB, self)._init(*args, **kwargs)
        self.version()
        
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
        commandExecutionDetails = self._sendInterfaceCommand(
                             self._modemCommands['read_register'], command)
        return self._waitForCommandToFinish(commandExecutionDetails,
                                             timeout=timeout)

    def _readInterface(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read()
        if len(responses) != 0:
            self._logger.debug("[UPB] Response>\n" + hex_dump(responses) + "\n")
            for response in responses.splitlines():
                responseCode = response[:2]
                if responseCode == 'PA':  # UPB Packet was received by PIM. No ack yet
                    #pass
                    self._processUBP(response, lastPacketHash)
                elif responseCode == 'PU':  # UPB Unsolicited packet received
                    self._processNewUBP(response)
                elif responseCode == 'PK':  # UPB Packet was acknowledged
                    pass
                elif responseCode == 'PN':  # UPB Packet was not acknowledged
                    pass
#                    self._processUBP(response, lastPacketHash)
                elif responseCode == 'PR':  # Register read response
                    self._processRegister(response, lastPacketHash)
        else:
#            self._logger.debug('Sleeping')
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
            try:
                del self._pendingCommandDetails[foundCommandHash]
                self._logger.debug("Command %s completed\n" % foundCommandHash)
            except:
                self._logger.error("Command %s couldnt be deleted!\n" % foundCommandHash)
        else:
            self._logger.debug("Unable to find pending command details for the following packet:\n")
            self._logger.debug(hex_dump(response, len(response)) + "\n")

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
            try:
                del self._pendingCommandDetails[foundCommandHash]
                self._logger.debug("Command %s completed\n" % foundCommandHash)
            except:
                self._logger.error("Command %s couldnt be deleted!\n" % foundCommandHash)
        else:
            self._logger.debug("Unable to find pending command details for the following packet:\n")
            self._logger.debug(hex_dump(response, len(response)) + "\n")

    def _processNewUBP(self, response):
        command = 0x00
        self._logger.debug("Incoming message: " + response)
        incoming = UPBMessage()
        try:
            incoming.decode(response)
        except Exception, ex:
            self._logger.error("UPB Error decoding message -Incoming message: " + response +"=="+ str(ex))
        self._logger.debug('UPBN:' + str(incoming.network) + ":" + str(incoming.source) + ":" + str(incoming.destination) + ":" + Conversions.int_to_hex(incoming.message_did))
        address = (incoming.network, incoming.source)
        if incoming.message_did == UPBMessage.MessageDeviceControl.goto \
            or incoming.message_did == UPBMessage.MessageDeviceControl.fade_start \
            or incoming.message_did == UPBMessage.MessageDeviceControl.state_response:
            if Conversions.hex_to_int(incoming.message_data[1:2]) > 0:
                command = Command.ON
            else:
                command = Command.OFF
        elif incoming.message_did == UPBMessage.MessageDeviceControl.activate:
            address = (incoming.network, incoming.destination, 'L')
            command = Command.ON
        elif incoming.message_did == UPBMessage.MessageDeviceControl.deactivate:
            address = (incoming.network, incoming.destination, 'L')
            command = Command.OFF
        elif incoming.message_did == UPBMessage.MessageDeviceControl.report_state: 
            command = Command.STATUS
        if command:
            self._onCommand(command, address)

    def _device_goto(self, address, level, timeout=None, rate=None):
        message = UPBMessage()
        message.network = address[0]
        message.destination = address[1]
#        message.message_eid = UPBMessage.MessageDeviceControl.goto
        message.message_did = UPBMessage.MessageDeviceControl.goto
        message.message_data = Conversions.int_to_ascii(level)
        if rate != None:
            message.message_data = message.message_data + \
                                    Conversions.int_to_ascii(rate)
        command = message.to_hex()
        command = command + Conversions.hex_to_ascii('0D')
        commandExecutionDetails = self._sendInterfaceCommand(
                             self._modemCommands['send_upb'], command)
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)

    def _link_activate(self, address, timeout=None):
        message = UPBMessage()
        message.link_type = UPBMessage.LinkType.link
        message.network = address[0]
        message.destination = address[1]
#        message.message_eid = UPBMessage.MessageDeviceControl.goto
        message.message_did = UPBMessage.MessageDeviceControl.activate
        command = message.to_hex()
        command = command + Conversions.hex_to_ascii('0D')
        commandExecutionDetails = self._sendInterfaceCommand(
                             self._modemCommands['send_upb'], command)
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)        

    def _link_deactivate(self, address, timeout=None):
        message = UPBMessage()
        message.link_type = UPBMessage.LinkType.link
        message.network = address[0]
        message.destination = address[1]
#        message.message_eid = UPBMessage.MessageDeviceControl.goto
        message.message_did = UPBMessage.MessageDeviceControl.deactivate
        command = message.to_hex()
        command = command + Conversions.hex_to_ascii('0D')
        commandExecutionDetails = self._sendInterfaceCommand(
                             self._modemCommands['send_upb'], command)
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)


    def status(self, address, timeout=None):
        message = UPBMessage()
        message.network = address[0]
        message.destination = address[1]
#        message.message_eid = UPBMessage.MessageDeviceControl.goto
        message.message_did = UPBMessage.MessageDeviceControl.report_state
        command = message.to_hex()
        command = command + Conversions.hex_to_ascii('0D')
        commandExecutionDetails = self._sendInterfaceCommand(
                             self._modemCommands['send_upb'], command)
        return self._waitForCommandToFinish(commandExecutionDetails, timeout=timeout)      

    def on(self, address, timeout=None, rate=None):
        if len(address) <= 2:
            return self._device_goto(address, 0x64, timeout=timeout)
        else: # Device Link
            return self._link_activate(address, timeout=timeout)

    def off(self, address, timeout=None, rate=None):
        if len(address) <= 2:
            return self._device_goto(address, 0x00, timeout=timeout)
        else: # Device Link
            return self._link_deactivate(address, timeout=timeout)
    
    def level(self, address, level, timeout=None, rate=None):
        if len(address) <= 2:
            self._device_goto(address, level, timeout, rate)
        else: # Device Link
            if level >= 50:
                return self._link_activate(address, timeout=timeout)
            else:
                return self._link_deactivate(address, timeout=timeout)
        
    def __getattr__(self, name):
        name = name.lower()
        # Support levels of lighting
        if name[0] == 'l' and len(name) == 3:
            level = name[1:3]
            self._logger.debug("Level->{level}".format(level=level))
            level = int(level)
            return lambda x, y=None: self._device_goto(x, level, timeout=y ) 
        
        
    def version(self):
        self._logger.info("UPB Pytomation driver version " + self.VERSION + "\n")

    def _set_device_state(self, address, state):
        for d in self._devices:
            if d.address == address:
                d.state = state
