"""
File:
        maplinwirelesssocket.py

Description:

This is a helper class to generate the appropriate pulse train to turn on/off
wireless sockets sold by Maplins (based on a 433MHz sequence).

http://www.maplin.co.uk/p/remote-controlled-mains-sockets-5-pack-n38hn

You require a small transmitter module:
http://proto-pic.co.uk/434mhz-rf-link-transmitter/

This code will generate the appropriate pulse train as input to the above
component.

Inspiration was taken from https://github.com/dmcg/raspberry-strogonanoff and
http://www.fanjita.org/serendipity/archives/53-Interfacing-with-radio-controlled-mains-sockets-part-2.html
(the latter's domain has, at the time of writing, expired but I do have a copy
if anyone needs it).


Author(s):
         Colin Guthrie <colin@mageia.org>
         Copyright (c), 2013

License:
    This free software is licensed under the terms of the GNU public license, Version 3

Versions and changes:
    Initial version created May 2014

"""
import time

class MaplinWirelessSocket(object):

    _codes = [
        [0x33353335, 0x33533335, 0x35333335, 0x53333335],
        [0x33353353, 0x33533353, 0x35333353, 0x53333353],
        [0x33353533, 0x33533533, 0x35333533, 0x53333533],
        [0x33355333, 0x33535333, 0x35335333, 0x53335333]
    ]

    _on = 0x3333
    _off = 0x5333

    _pulseWidth = 450 * 1e-6 # Measured from Maplin transmitters

    _preamble = [0] * 26
    _sync = [1]
    _postamble = [0] * 2


    def __init__(self, onCallback, offCallback):
        self._onCallback = onCallback
        self._offCallback = offCallback


    # converts the lowest bit_count bits to a list of ints
    def _int2BitList(self, i, bitCount):
        result = []
        shifted = i
        for i in range(0, bitCount):
            result.append(shifted & 0x01)
            shifted = shifted >> 1
        return result


    def _commandAsBitList(self, channel, button, on):
        return \
            self._int2BitList(self._codes[channel - 1][button - 1], 32) + \
            self._int2BitList(self._on if on else self._off, 16)


    # encodes 0 as a 1 count state change, 1 as a 3 count state change, starting
    # with a change to low
    def _encodeStateList(self, bitList):
        result = []
        state = 0
        for bit in bitList:
            result.extend([state] if bit == 0 else [state, state, state])
            state = 1 - state
        return result


    def _busyWait(self, end):
        while (time.time() <= end): pass


    def _send(self, channel, button, on):
        bits = self._commandAsBitList(channel, button, on)
        states = self._preamble + self._sync + self._encodeStateList(bits) + self._postamble

        for i in xrange(1, 6):
            end = time.time()
            laststate = 2
            for state in states:
                end = end + self._pulseWidth
                if laststate != state:
                    if state:
                        self._onCallback()
                    else:
                        self._offCallback()
                    laststate = state
                self._busyWait(end)


    def on(self, channel, button):
        self._send(channel, button, 1)


    def off(self, channel, button):
        self._send(channel, button, 0)

