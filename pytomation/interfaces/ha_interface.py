'''
File:
        ha_interface.py

Description:


Author(s): 
         Pyjamasam@github <>
         Jason Sharpee <jason@sharpee.com>  http://www.sharpee.com

License:
    This free software is licensed under the terms of the GNU public license, Version 1     

Usage:


Example: 

Notes:


Created on Mar 26, 2011
'''
import hashlib
import threading
import time
import binascii
import sys
from collections import deque

from .common import *
from pytomation.common.pytomation_object import PytomationObject

class HAInterface(AsynchronousInterface, PytomationObject):
    "Base protocol interface"

    MODEM_PREFIX = '\x02'
    
    def __init__(self, interface, *args, **kwargs):
        kwargs.update({'interface': interface})
        self._po_common(*args, **kwargs)
        super(HAInterface, self).__init__(*args, **kwargs)


    def _init(self, *args, **kwargs):
        super(HAInterface, self)._init(*args, **kwargs)
        self._shutdownEvent = threading.Event()
        self._interfaceRunningEvent = threading.Event()

        self._commandLock = threading.Lock()
        self._outboundQueue = deque()
        self._outboundCommandDetails = dict()
        self._retryCount = dict()

        self._pendingCommandDetails = dict()

        self._commandReturnData = dict()

        self._intersend_delay = 0.15  # 150 ms between network sends
        self._lastSendTime = 0

        self._interface = kwargs['interface']
        self._commandDelegates = []
        self._devices = []
        self._lastPacketHash = None

    def shutdown(self):
        if self._interfaceRunningEvent.isSet():
            self._shutdownEvent.set()

            #wait 2 seconds for the interface to shut down
            self._interfaceRunningEvent.wait(2000)

    def run(self, *args, **kwargs):
        self._interfaceRunningEvent.set()

        #for checking for duplicate messages received in a row

        while not self._shutdownEvent.isSet():
            self._writeInterface()

            self._readInterface(self._lastPacketHash)

        self._interfaceRunningEvent.clear()

    def onCommand(self, callback=None, address=None, device=None):
        # Register a device for notification of commands
        if not device:
            self._commandDelegates.append({
                                       'address': address,
                                       'callback': callback,
                                       })
        else:
            self._devices.append(device)
    
    def _onCommand(self, command=None, address=None):
        # Received command from interface and this will delegate to subscribers
        self._logger.debug("Received Command:" + str(address) + ":" + str(command))
        self._logger.debug('Delegates for Command: ' + str(self._commandDelegates))
        
        addressC = address
        try:
            addressC = addressC.lower()
        except:
            pass
        for commandDelegate in self._commandDelegates:
            addressD = commandDelegate['address']
            try:
                addressD = addressC
            except:
                pass
            if commandDelegate['address'] == None or \
                addressD == addressC:
                    commandDelegate['callback'](
                                                command=command,
                                                address=address,
                                                source=self
                                                )
        self._logger.debug('Devices for Command: ' + str(self._commandDelegates))
        for device in self._devices:
            if device.addressMatches(address):
                try:
                    device._on_command(
                                       command=command,
                                       address=address,
                                       source=self,
                                       )
                except Exception, ex:
                    device.command(
                                   command=command,
                                   source=self,
                                   address=address)

    def _sendInterfaceCommand(self, modemCommand,
                          commandDataString=None,
                          extraCommandDetails=None, modemCommandPrefix=None):

        returnValue = False
        try:
            if self._interface.disabled == True:
                return returnValue
        except AttributeError, ex:
            pass

        try:
#            bytesToSend = self.MODEM_PREFIX + binascii.unhexlify(modemCommand)
            if modemCommandPrefix:
                bytesToSend = modemCommandPrefix + modemCommand
            else:
                bytesToSend = modemCommand
            if commandDataString != None:
                bytesToSend += commandDataString
            commandHash = hashPacket(bytesToSend)

            self._commandLock.acquire()
            if commandHash in self._outboundCommandDetails:
                #duplicate command.  Ignore
                pass

            else:
                waitEvent = threading.Event()

                basicCommandDetails = {'bytesToSend': bytesToSend,
                                       'waitEvent': waitEvent,
                                       'modemCommand': modemCommand}

                if extraCommandDetails != None:
                    basicCommandDetails = dict(
                                       basicCommandDetails.items() + \
                                       extraCommandDetails.items())

                self._outboundCommandDetails[commandHash] = basicCommandDetails

                self._outboundQueue.append(commandHash)
                self._retryCount[commandHash] = 0

                self._logger.debug("Queued %s" % commandHash)

                returnValue = {'commandHash': commandHash,
                               'waitEvent': waitEvent}

            self._commandLock.release()

        except Exception, ex:
            print traceback.format_exc()

        finally:

            #ensure that we unlock the thread lock
            #the code below will ensure that we have a valid lock before we call release
            self._commandLock.acquire(False)
            self._commandLock.release()

        return returnValue

    def _writeInterface(self):
        #check to see if there are any outbound messages to deal with
        self._commandLock.acquire()
        if self._outboundQueue and (len(self._outboundQueue) > 0) and \
            (time.time() - self._lastSendTime > self._intersend_delay):
            commandHash = self._outboundQueue.popleft()

            try:
                commandExecutionDetails = self._outboundCommandDetails[commandHash]
            except Exception, ex:
                self._logger.error('Could not find execution details: {command} {error}'.format(
                                                                                                command=commandHash,
                                                                                                error=str(ex))
                                   )
            else:
                bytesToSend = commandExecutionDetails['bytesToSend']
    
    #            self._logger.debug("Transmit>" + str(hex_dump(bytesToSend, len(bytesToSend))))
                try:
                    self._logger.debug("Transmit>" + Conversions.ascii_to_hex(bytesToSend))
                except:
                    self._logger.debug("Transmit>" + str(bytesToSend))
                    
#                result = self._interface.write(bytesToSend)
                result = self._writeInterfaceFinal(bytesToSend)
                self._logger.debug("TransmitResult>" + str(result))
    
                self._pendingCommandDetails[commandHash] = commandExecutionDetails
                del self._outboundCommandDetails[commandHash]
    
                self._lastSendTime = time.time()

        try:
            self._commandLock.release()
        except Exception, te:
            self._logger.debug("Error trying to release unlocked lock %s" % (str(te)))

    def _writeInterfaceFinal(self, data):
        return self._interface.write(data)

    def _readInterface(self, lastPacketHash):
        response = None
        #check to see if there is anyting we need to read
        if self._interface:
            response = self._interface.read()
        try:
            if response and len(response) != 0:
    #            self._logger.debug("[HAInterface-Serial] Response>\n" + hex_dump(response))
                self._logger.debug("Response>" + hex_dump(response) + "<")
                self._onCommand(command=response)
            else:
                #print "Sleeping"
                #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
                #time.sleep(0.1)
                time.sleep(0.5)
        except TypeError, ex:
            pass

    def _waitForCommandToFinish(self, commandExecutionDetails, timeout=None):

        if type(commandExecutionDetails) != type(dict()):
            self._logger.error("Unable to wait without a valid commandExecutionDetails parameter")
            return False

        waitEvent = commandExecutionDetails['waitEvent']
        commandHash = commandExecutionDetails['commandHash']

        realTimeout = 2  # default timeout of 2 seconds
        if timeout:
            realTimeout = timeout

        timeoutOccured = False

        if sys.version_info[:2] > (2, 6):
            #python 2.7 and above waits correctly on events
            timeoutOccured = not waitEvent.wait(realTimeout)
        else:
            #< then python 2.7 and we need to do the waiting manually
            while not waitEvent.isSet() and realTimeout > 0:
                time.sleep(0.1)
                realTimeout -= 0.1

            if realTimeout == 0:
                timeoutOccured = True

        if not timeoutOccured:
            if commandHash in self._commandReturnData:
                return self._commandReturnData[commandHash]
            else:
                return True
        else:
            #re-queue the command to try again
            self._commandLock.acquire()

            if self._retryCount[commandHash] >= 5:
                #too many retries.  Bail out
                self._commandLock.release()
                return False

            self._logger.debug("Timed out for %s - Requeueing (already had %d retries)" % \
                (commandHash, self._retryCount[commandHash]))

            requiresRetry = True
            if commandHash in self._pendingCommandDetails:
                self._outboundCommandDetails[commandHash] = \
                    self._pendingCommandDetails[commandHash]

                del self._pendingCommandDetails[commandHash]

                self._outboundQueue.append(commandHash)
                self._retryCount[commandHash] += 1
            else:
                self._logger.debug("Interesting.  timed out for %s, but there are no pending command details" % commandHash)
                #to prevent a huge loop here we bail out
                requiresRetry = False

            try:
                self._logger.debug("Removing Lock " + str( self._commandLock))
                self._commandLock.release()
            except:
                self._logger.error("Could not release Lock! " + str(self._commandLock))
                
            if requiresRetry:
                return self._waitForCommandToFinish(commandExecutionDetails,
                                                    timeout=timeout)
            else:
                return False

    @property
    def name(self):
        return self.name_ex
    
    @name.setter
    def name(self, value):
        self.name_ex = value
        return self.name_ex
    
    def update_status(self):
        for d in self._devices:
            self.status(d.address)
            
    def status(self, address=None):
        return None
