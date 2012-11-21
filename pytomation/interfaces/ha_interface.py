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
from ..config import *

class HAInterface(AsynchronousInterface):
    "Base protocol interface"

    MODEM_PREFIX = '\x02'
    
    def __init__(self, interface, *args, **kwargs):
        super(HAInterface, self).__init__(interface=interface)

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

    def shutdown(self):
        if self._interfaceRunningEvent.isSet():
            self._shutdownEvent.set()

            #wait 2 seconds for the interface to shut down
            self._interfaceRunningEvent.wait(2000)

    def run(self):
        self._interfaceRunningEvent.set()

        #for checking for duplicate messages received in a row
        lastPacketHash = None

        while not self._shutdownEvent.isSet():
            self._writeModem()

            self._readModem(lastPacketHash)

        self._interfaceRunningEvent.clear()

    def onCommand(self, callback=None, address=None):
        self._commandDelegates.append({
                                   'address': address,
                                   'callback': callback,
                                   })

    def _onCommand(self, command=None, address=None):
        if debug['HAInterface'] > 0:
            print "[HAInterface] Received Command:" + str(address) + ":" + str(command)
        for commandDelegate in self._commandDelegates:
            if commandDelegate['address'] == None or \
                commandDelegate['address'] == address:
                    commandDelegate['callback'](
                                                command=command,
                                                address=address,
                                                source=self
                                                )

    def _sendModemCommand(self, modemCommand,
                          commandDataString=None,
                          extraCommandDetails=None, modemCommandPrefix=None):

        returnValue = False

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

                if debug['Serial'] > 0:
                    print "[HAInterface-Serial] Queued %s" % commandHash

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

    def _writeModem(self):
        #check to see if there are any outbound messages to deal with
        self._commandLock.acquire()
        if (len(self._outboundQueue) > 0) and \
            (time.time() - self._lastSendTime > self._intersend_delay):
            commandHash = self._outboundQueue.popleft()

            commandExecutionDetails = self._outboundCommandDetails[commandHash]

            bytesToSend = commandExecutionDetails['bytesToSend']
            if debug['Serial'] > 0:
                print "[HAInterface-Serial] Transmit>\n", hex_dump(bytesToSend, len(bytesToSend)),

            self._interface.write(bytesToSend)

            self._pendingCommandDetails[commandHash] = commandExecutionDetails
            del self._outboundCommandDetails[commandHash]

            self._lastSendTime = time.time()

        self._commandLock.release()

    def _readModem(self, lastPacketHash):
        #check to see if there is anyting we need to read
        response = self._interface.read()
        if len(response) != 0:
            if debug['Serial'] > 0:
                print "[HAInterface-Serial] Response>\n" + hex_dump(response)
        else:
            #print "Sleeping"
            #X10 is slow.  Need to adjust based on protocol sent.  Or pay attention to NAK and auto adjust
            #time.sleep(0.1)
            time.sleep(0.5)

    def _waitForCommandToFinish(self, commandExecutionDetails, timeout=None):

        if type(commandExecutionDetails) != type(dict()):
            print "Unable to wait without a valid commandExecutionDetails parameter"
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

            print "Timed out for %s - Requeueing (already had %d retries)" % \
                (commandHash, self._retryCount[commandHash])

            requiresRetry = True
            if commandHash in self._pendingCommandDetails:
                self._outboundCommandDetails[commandHash] = \
                    self._pendingCommandDetails[commandHash]

                del self._pendingCommandDetails[commandHash]

                self._outboundQueue.append(commandHash)
                self._retryCount[commandHash] += 1
            else:
                print "Interesting.  timed out for %s, but there is no pending command details" % commandHash
                #to prevent a huge loop here we bail out
                requiresRetry = False

            self._commandLock.release()

            if requiresRetry:
                return self._waitForCommandToFinish(commandExecutionDetails,
                                                    timeout=timeout)
            else:
                return False
