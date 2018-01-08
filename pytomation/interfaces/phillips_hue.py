"""
File: 
    phillips_hue.py

George Farris <farrisg@gmsys.com>
Copyright (c), 2015

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.



Description:

This is a driver for the Phillips HUE colour LED interface.  The HUE supports
a number of devices such as 120VAC LED lights, Low voltage LED strips, wireless
dimmer switches to name a few.  

This driver uses the phue library created by Nathanael Lecaude and can be
found at:
        https://github.com/studioimaginaire/phue

Author(s):
         George Farris <farrisg@gmsys.com>
         Copyright (c), 2015

License:
    This free software is licensed under the terms of the GNU public license, 
    Version 3

Versions and changes:
    Initial version created on Nov 29, 2015
    Nov 29, 2015 - 1.0 - Initial version
    Jan 06, 2016 - 1.1 - Added support for groups
    Jan 09, 2016 - 1.2 - Added update_status command
    Jan 25, 2016 - 1.3 - Updated status check so it won't trigger unless required
    
"""
import threading
import time
import re
from Queue import Queue
from binascii import unhexlify
from phue import Bridge

from .common import *
from .ha_interface import HAInterface


class PhillipsHue(HAInterface):
    VERSION = '1.3'
    valid_commands = ('bri','hue','sat','ct','rgb','tr','eft')        
    
    def __init__(self, *args, **kwargs):
        super(PhillipsHue, self).__init__(None, *args, **kwargs)
        
    # Instance should be hue = PhillipsHue(address = '192.168.0.2', poll=10)
    def _init(self, *args, **kwargs):
        super(PhillipsHue, self)._init(*args, **kwargs)
        self._iteration = 0
        self._poll_secs = kwargs.get('poll', 60)
        self.last_status = {}
                
        # get the ip address and connect to the bridge
        self._ip = kwargs.get('address', None)
        print "Phillips HUE Bridge address -> {0}".format(self._ip)
        try:
            self.interface = Bridge(self._ip)
            self.interface.connect()
            self._logger.debug("[Hue] Connected to interface at {0}...\n".format(self._ip))
        except Exception, ex:
            self._logger.debug('[Hue] Could not connect to bridge: {0}'.format(str(ex)))
            print "\nCouldn't connect to HUE bridge, please press the LINK button\n"
            print "on the bridge and restart Pytomation within 30 seconds..."
            sys.exit()
                        
        # Get the initial configuration of the Bridge so we can see models of lights etc
        # self.bridge_config['lights']['1']['modelid']
        # Eventually we will build a table of device capabilites, for example if the 
        # light is dimmable
        self.bridge_config = self.interface.get_api()
        #devices = self._build_device_table()
        self.version()

    def _readInterface(self, lastPacketHash):
        # We need to dial back how often we check the bridge.. Lets not bombard it!
        if not self._iteration < self._poll_secs:
            self._logger.debug('[HUE] Retrieving status from bridge.')
            self._iteration = 0
            #check to see if there is anything we need to read
            try:
                # get dictionary of lights
                lights = self.interface.get_light_objects('id')
                #print lights
                for d in self._devices:
                    #print d.address,d.state,lights[int(d.address[1:])].on
                    if d.state == 'off' and lights[int(d.address[1:])].on == True:
                        time.sleep(.01)     #wait 10ms to see if state will change
                        if d.state == 'off' and lights[int(d.address[1:])].on == True:
                            contact = Command.OFF
                            self._logger.debug('Light {0} status -> {1}'.format(d.address, contact))
                            self._onCommand(address="{0}".format(d.address),command=contact)
                    elif d.state == 'on' and lights[int(d.address[1:])].on == False:
                        time.sleep(.01)     #wait 10ms to see if state will change
                        if d.state == 'on' and lights[int(d.address[1:])].on == False:
                            bri = int(round(int(lights[l].brightness) / 255.0 * 100))                        
                            contact = (Command.LEVEL, bri)
                            self._logger.debug('Light {0} status -> {1}'.format(d.address, contact))
                            self._onCommand(address="{0}".format(d.address),command=contact)    
            except Exception, ex:
                self._logger.error('Could not process data from bridge: '+ str(ex))

        else:
            self._iteration+=1
            time.sleep(1) # one sec iteration

                 
    def on(self, address):
        # TODO Check the type of bulb and then command accordingly
        
        # an 'on' command always sets level to 100% and colour to white
        cmd =  {'transitiontime' : 0, 'on' : True, 'bri' : 255, 'ct' : 370}
        
        if address[:1] == 'L':
            result = self.interface.set_light(int(address[1:]), cmd)
        elif address[:1] == 'G':
            result = self.interface.set_group(int(address[1:]), cmd)            
        else:
            self._logger.error("{name} not a valid HUE address {addr}".format(
                                                                                name=self.name,
                                                                                addr=address,
                                                                                ))
            return
        # TODO parse result 


    def off(self, address):
        cmd =  {'transitiontime' : 0, 'on' : False}
        if address[:1] == 'L':
            result = self.interface.set_light(int(address[1:]), cmd)
        elif address[:1] == 'G':
            result = self.interface.set_group(int(address[1:]), cmd)            
        else:
            self._logger.error("{name} not a valid HUE address {addr}".format(
                                                                                    name=self.name,
                                                                                    addr=address,
                                                                                     ))
            return

        
    # Level for the HUE is capable of setting the following:
    #   brightness : level = (int) - int is from 0 to 100 (mapped to 255) 
    #   hue        : level = ('hue':int') - int is from 0 to 65535
    #   saturation : level = ('sat':int') - int is from 0 to 255    
    #   hue and sat: level = ('hue':int', 'sat:int') - int is from 0 to 65535
    #   ct         : level = ('ct':int') - int is from 153 to 500
    #   rgb        : level = ('rgb':hex) - hex is from 000000 to ffffff
    #   transition : level = ('tr':int') int is from 0 to 3000 in 1/10 seconds
    #   effect     : level = ('eft':colorloop|none') put bulb in colour loop
    # Not all RGB colours will produce a colour in the HUE lamps.
    # ct values are translated kelvin temperature values from 2000K to 6500K
    # 2000K maps to 500 and 6500K maps to 153
    # If the lamp is already on don't send an on command
    
    # TODO check if bulb type can perform the selected operation
    def level(self, address, level, timeout=None, rate=None):
        cmd = {}
        #print level
        if (isinstance(level, tuple)):
            for i in level:
                if isinstance(i, int):    #classic pytomation brightness
                    i = 'bri:{0}'.format(i)
                cmd = dict(self._build_hue_command(i).items() + cmd.items())
            #print cmd    
            if address[:1] == 'L':
                result = self.interface.set_light(int(address[1:]), cmd)
            elif address[:1] == 'G':
                result = self.interface.set_group(int(address[1:]), cmd)            
            else:
                self._logger.error("{name} not a valid HUE address {addr}".format(
                                                                                    name=self.name,
                                                                                    addr=address,
                                                                                     ))
                return

        else:
            if isinstance(level, int):    #classic pytomation brightness
                level = 'bri:{0}'.format(level)
            
            if  level.split(':')[0] not in self.valid_commands:
                self._logger.error("{name} not a valid HUE command {level}".format(
                                                                                    name=self.name,
                                                                                    level=level,
                                                                                     ))
                return
            cmd = self._build_hue_command(level)
            if address[:1] == 'L':
                result = self.interface.set_light(int(address[1:]), cmd)
            elif address[:1] == 'G':
                result = self.interface.set_group(int(address[1:]), cmd)            
            else:
                self._logger.error("{name} not a valid HUE address {addr}".format(
                                                                                    name=self.name,
                                                                                    addr=address,
                                                                                     ))
                return
        
    def hue(self, address):
        pass
        
    def saturation(self, address):
        pass

    def _build_hue_command(self, level):
        if (isinstance(level, tuple)):
            pass
        else:
            huecmd = level.split(':')[0]
            hueval = level.split(':')[1]
            if huecmd == 'bri':
                hueval = int(hueval)
                if self._check_range(huecmd, hueval, 0, 100):
                    # if level is 0 or 1 turn hue off
                    if hueval == 0 or hueval == 1:
                        return {'on' : False}
                    else:
                        # make it 0 to 255                                                                                     
                        brimapped = int((int(hueval) / 100.0) * int(0xFF))
                        return {'on' : True, huecmd : brimapped}
                else:
                    return None
                
            elif huecmd == 'hue':
                hueval = int(hueval)
                if self._check_range(huecmd, hueval, 0, 65535):
                    return {'on' : True, huecmd : hueval}
                else:
                    return None
                
            elif huecmd == 'sat':
                hueval = int(hueval)
                if self._check_range(huecmd, hueval, 0, 255):
                    return {'on' : True, huecmd : hueval}
                else:
                    return None
                
            elif huecmd == 'ct':
                hueval = int(hueval)
                if self._check_range(huecmd, hueval, 153, 500):
                    return {'on' : True, huecmd : hueval}
                else:
                    return None

            elif huecmd == 'tr':
                hueval = int(hueval)
                if self._check_range(huecmd, hueval, 0, 3000):
                    return {'on' : True, 'transitiontime' : hueval}
                else:
                    return None
                
            elif huecmd == 'rgb':
                if self._check_range(huecmd, int(hueval, 16), 0, 16777215):
                    xy = ()   # no colour               
                    # convert the hex colour ('000000' to 'ffffff') to RGB
                    red = int(hueval[0:2], 16)    #red
                    green = int(hueval[2:4], 16)  #green
                    blue = int(hueval[4:6], 16)   #blue
                    xy = self._rgb2xy(red, green, blue)

                    return {'on' : True, 'xy' : xy}
                else:
                    return None

            elif huecmd == 'eft':
                if hueval == 'colorloop' or hueval == 'none':
                    return {'on' : True, 'effect' : hueval}
                else:
                    return None

    def update_status(self):
        lights = self.interface.get_light_objects('id')
        for d in self._devices:
            print "Getting status for HUE -> ", d.address
            if lights[int(d.address[1:])].on == True:
                bri = int(round(int(lights[int(d.address[1:])].brightness) / 255.0 * 100))                        
                contact = (Command.LEVEL, bri)
            else:
                contact = Command.OFF
            self._logger.debug('Light L{0} status -> {1}'.format(d.address, contact))
            self._onCommand(address="{0}".format(d.address),command=contact)


    def _check_range(self, cmd, val, minv, maxv):
        if val > maxv or val < minv:
            self._logger.error("hue cannot set {level} beyond {mn} - {mx}".format(level=cmd,
                                                                                    mn=minv,
                                                                                    mx=maxv,
                                                                                     ))
            return False
        else:
            return True
            

    def _rgb2xy(self, red, green, blue):
        # Returns xy point containing the closest available gamut colour (cie 1931)
    
        r = ((red + 0.055) / (1.0 + 0.055))**2.4 if (red > 0.04045) else (red / 12.92)
        g = ((green + 0.055) / (1.0 + 0.055))**2.4 if (green > 0.04045) else (green / 12.92)
        b = ((blue + 0.055) / (1.0 + 0.055))**2.4 if (blue > 0.04045) else (blue / 12.92)
    
        x = r * 0.4360747 + g * 0.3850649 + b * 0.0930804
        y = r * 0.2225045 + g * 0.7168786 + b * 0.0406169
        z = r * 0.0139322 + g * 0.0971045 + b * 0.7141733
    
        if x + y + z == 0:
            cx = cy = 0
        else:
            cx = x / (x + y + z)
            cy = y / (x + y + z)
    
        # Check if the given xy value is within the colour reach of our lamps.
        xyPoint = cx, cy,

        return xyPoint


    def version(self):
        self._logger.info("Phillips HUE Pytomation driver version " + self.VERSION + '\n')

