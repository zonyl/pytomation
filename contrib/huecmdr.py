#! /usr/bin/python2
#-------------------------------------------------------------------------------
#  Huecmdr - Phillips HUE Bridge Utility
#
#  Copyright (c) 2016 George Farris - farrisg@gmsys.com
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#-------------------------------------------------------------------------------

# Release history
# Jan 04, 2016 - V1.0  Initial release
# Jan 05, 2016 - V1.1  Remove test values left in by mistake.
# Jan 07, 2016 - V1.2  Added Group support and light on/off in colours


import curses, time, sys, math, datetime
import json, os, socket, httplib

from phue import Bridge
from colorpy import colormodels
from collections import namedtuple

# Registering with your HUE Bridge from Python
# 1) from phue import Bridge
# 2) Press link button on Bridge
# 3) b=Bridge('ip address of bridge')
# 4) b.connect()
# You must run commands 3 and 4 within 30 seconds of pushing the button

IP_ADDRESS = None

#================= End of user setable values ================================
VERSION = '1.2'
VERSION_DATE = 'Jan 07,2016'

CURSOR_INVISIBLE = 0    # no cursor
CURSOR_NORMAL = 1       # Underline cursor
CURSOR_BLOCK = 2        # Block cursor
NOCHAR = -1


# Represents a CIE 1931 XY coordinate pair.
XYPoint = namedtuple('XYPoint', ['x', 'y'])
Red = XYPoint(0.675, 0.322)
Green = XYPoint(0.4091, 0.518)
Blue = XYPoint(0.167, 0.04)


class Hue():

    def __init__(self):
        self.logio = False        
        self.ip = None
        self.username = None
        self.light = None
        self.group = None
        
    def setup_screen(self):
        cur = curses.initscr()  # Initialize curses.
        curses.cbreak()
        curses.noecho()
        curses.nonl()
        cur.refresh()
        screen = curses.newwin(25,80)
        screen.nodelay(1)
        screen.keypad(1)
        screen.scrollok(True)
        screen.idlok(1)
        screen.refresh()
        return screen
        
    def terminate(self):
        curses.endwin()
        sys.exit()

    def check_hue_bridge(self, scn):
        scn.addstr(1,5,"Phillips HUE Bridge authentication...")
    
        scn.addstr(9,5,"You haven't set the IP address for your Phillips HUE Bridge...")
        scn.addstr(11,5, "If you have never used the Bridge on this computer, you ")
        scn.addstr(12,5, "will have to authorize it.")
        scn.addstr(15,5,"Hit any key to continue...")
        scn.nodelay(0)
        k = scn.getch()
        scn.erase()
        scn.refresh()

    #stdscr.addstr(12,5,"Follow this link to easily authorize your computer with your web browser.")
    #stdscr.addstr(13,5,"http://www.developers.meethue.com/documentation/getting-started")

    # not an exact reverse of rgb2xy
    def xy2rgb(self, x, y, bri=1):
        xyPoint = XYPoint(x, y)

        # Calculate XYZ values Convert using the following formulas:
        Y = bri
        X = (Y / xyPoint.y) * xyPoint.x
        Z = (Y / xyPoint.y) * (1 - xyPoint.x - xyPoint.y)

        # Convert to RGB using Wide RGB D65 conversion.
        r =  X * 1.612 - Y * 0.203 - Z * 0.302
        g = -X * 0.509 + Y * 1.412 + Z * 0.066
        b =  X * 0.026 - Y * 0.072 + Z * 0.962

        # Apply reverse gamma correction.
        r, g, b = map(
            lambda x: (12.92 * x) if (x <= 0.0031308) else ((1.0 + 0.055) * pow(x, (1.0 / 2.4)) - 0.055),
            [r, g, b]
        )

        # Bring all negative components to zero.
        r, g, b = map(lambda x: max(0, x), [r, g, b])

        # If one component is greater than 1, weight components by that value.
        max_component = max(r, g, b)
        if max_component > 1:
            r, g, b = map(lambda x: x / max_component, [r, g, b])

        r, g, b = map(lambda x: int(x * 255), [r, g, b])

        return (r, g, b)


    def rgb2xy(self, red, green, blue):
    
        r = ((red + 0.055) / (1.0 + 0.055))**2.4 if (red > 0.04045) else (red / 12.92)
        g = ((green + 0.055) / (1.0 + 0.055))**2.4 if (green > 0.04045) else (green / 12.92)
        b = ((blue + 0.055) / (1.0 + 0.055))**2.4 if (blue > 0.04045) else (blue / 12.92)
    
        X = r * 0.4360747 + g * 0.3850649 + b * 0.0930804
        Y = r * 0.2225045 + g * 0.7168786 + b * 0.0406169
        Z = r * 0.0139322 + g * 0.0971045 + b * 0.7141733
    
        if X + Y + Z == 0:
            cx = cy = 0
        else:
            cx = X / (X + Y + Z)
            cy = Y / (X + Y + Z)
    
        xyPoint = XYPoint(cx, cy)
        return xyPoint

    def tohex(self, r, g, b):
        #Convert to hex string
        s = ['#',hex(int(r))[2:].zfill(2), hex(int(g))[2:].zfill(2), hex(int(b))[2:].zfill(2)]
        for item in enumerate(s):
            if item[1]=='100':
                s[item[0]]='ff'
        return ''.join(s)

    def showdata(self, scn, data):
        wy,wx=scn.getmaxyx()
        
        if type(data) == str:
            data = data.split('\n')
        
        pady = max(len(data)+1,wy)
        padx = wx

        max_x = wx
        max_y = pady-wy
                
        pad = curses.newpad(pady,padx)
            
        for i,line in enumerate(data):
            pad.addstr(i,0,str(line))
        
        scn.refresh()
        
        x=0
        y=0

        scn.nodelay(0)
        while True:
            pad.refresh(y,x,0,0,wy-1,wx)
            c = scn.getch()

            if curses.keyname(c) == 'q':
                break
            if c == curses.KEY_DOWN:
                y=min(y+1,max_y)
            if c == curses.KEY_UP:
                y=max(y-1,0)

                

        curses.flushinp()
        pad.clear()
        scn.nodelay(1)
        scn.touchwin()
        scn.refresh()


    def request(self, scn, mode='GET', address=None, data=None):
        connection = httplib.HTTPConnection(self.ip, timeout=10)

        try:
            if mode == 'GET' or mode == 'DELETE':
                connection.request(mode, address)
            if mode == 'PUT' or mode == 'POST':
                connection.request(mode, address, data)

        except socket.timeout:
            error = "{} Request to {} timed out.".format(mode, self.ip)
            raise PhueRequestTimeout(None, error)

        result = connection.getresponse()

        connection.close()
        result_str = result.read()

        return json.loads(result_str)

    def authenticate(self, scn):
        scn.erase()
        scn.refresh()
        
        scn.addstr(1,5,"Phillips HUE Bridge authentication...")
    
        scn.addstr(9,5,"You haven't set the IP address for your Phillips HUE Bridge...")
        scn.addstr(11,5, "If you have never used the Bridge on this computer, you ")
        scn.addstr(12,5, "will have to authorize it.")
        scn.addstr(15,5,"What is the IP address of your Bridge? ")
        scn.nodelay(0)
        curses.echo()
        ip = scn.getstr()
        scn.addstr(17,5,"Trying to connect to " + ip)
        scn.addstr(18,5,"Press button on Bridge then hit Enter...")
        scn.nodelay(0)
        k = scn.getch()
                
        try:
            hub = Bridge(ip)
        except:
            scn.addstr(20,5, "Error connecting to Bridge, check your IP address and try again.")
            scn.addstr(21,5, "Hit any key to go to menu.")
            k = scn.getch()
            scn.erase()
            scn.refresh()
            hub = False
        return hub

# $ ./huecmdr.py 
# [{u'success': {u'/lights': u'Searching for new devices'}}]
#{u'lastscan': u'2015-12-31T21:16:43'}

# $ ./huecmdr.py 
# [{u'success': {u'/lights': u'Searching for new devices'}}]
# {u'lastscan': u'2015-12-31T21:18:52', u'5': {u'name': u'Hue white lamp 2'}}

    def add_new_bulb(self, scn, hub):
        lights = self.request(scn, 'POST', '/api/' + self.username + '/lights/')
        try:
            popup = curses.newwin(7, 40, 10, 20)
            popup.addstr(2, 5, "Searching for new lights...")
            popup.border('|','|','-','-','+','+','+','+')
            popup.nodelay(0)
            curses.curs_set(CURSOR_INVISIBLE)
            popup.refresh()
        except:
            pass
        
        t = 70
        while t:
            popup.addstr(2,34,"{0:<2}".format(t))
            popup.refresh()
            time.sleep(1)
            t -= 1 
        newlights = self.request(scn,'GET', '/api/' + self.username + '/lights/new')
        
        if len(newlights) > 1:
            popup.addstr(3,5, "Found new lights...", curses.A_BOLD)
            popup.addstr(4,5, "Press any key to continue...")
            c = popup.getch()
            popup.refresh()
            self.list_bulbs(scn, hub)
        else:
            popup.addstr(3,5, "No new lights found...")
            popup.addstr(4,5, "Press any key to continue...")
            c = popup.getch()
            popup.refresh()
        curses.curs_set(CURSOR_NORMAL)
        scn.touchwin()
        scn.refresh()
        
    def adjust_colours(self, scn, hub):
        if self.light == None and self.group == None:
            self.popup_error(scn, "You haven't selected a light or group yet...")
            return
        value = [0,0,0,0,0,0,0,0,0]
        data = ('Hue             :', 'Saturation      :',' ',\
                'Red             :', 'Green           :', 'Blue            :', ' ',\
                'Temperature     :', 'Brightness      :')
        popup = self.popup_colour_dialog(scn, hub, data, 'Adjust HUE colours')

        idx = 0
        popup.addstr(idx+3,9,data[idx],curses.A_REVERSE)
        popup.addstr(idx+3,36,'[  Light or Group  ]')
        popup.addstr(idx+4,36,'[ 00 ] [ ON ][ OFF ]')
        if self.light != None:
            state = hub.get_light(self.light, 'on')

            value[0] = hub.get_light(self.light, 'hue')
            popup.addstr(3,28,str(value[0]))
            value[1] = hub.get_light(self.light, 'sat')
            popup.addstr(4,28,str(value[1]))

            value[7] = hub.get_light(self.light, 'ct')
            popup.addstr(10,28,str(value[7]))
            value[8] = hub.get_light(self.light, 'bri')
            popup.addstr(11,28,str(value[8]))

            xy = hub.get_light(self.light, 'xy')
            value[3],value[4],value[5] = self.xy2rgb(xy[0], xy[1], value[8])
            popup.addstr(6,28,str(value[3]))
            popup.addstr(7,28,str(value[4]))
            popup.addstr(8,28,str(value[5]))

        else:  # it's a group
            state = hub.get_group(self.group, 'on')
            popup.addstr(4,38,"{0:0>2}".format(self.group))

        if state:
            popup.addstr(4,45,'ON', curses.A_REVERSE)
        else:
            popup.addstr(4,51,'OFF', curses.A_REVERSE)
        
        popup.addstr(6, 35,"-+")
        popup.addstr(7, 35," |--Hex value->")
        popup.addstr(8, 35,"-+")

        while True:
            c = popup.getch()

            if c == curses.KEY_DOWN:
                if idx + 1 < len(data):
                    popup.addstr(idx+3,9,data[idx],curses.A_NORMAL)
                    if idx == 1 or idx == 5:
                        idx += 2
                    else:
                        idx += 1
                    popup.addstr(idx+3,9,data[idx],curses.A_REVERSE)
                    popup.refresh()
            elif c == curses.KEY_UP:
                if idx -1 >= 0:
                    popup.addstr(idx+3,9,data[idx],curses.A_NORMAL)
                    if idx == 3 or idx == 7:
                        idx -= 2
                    else:
                        idx -= 1
                    popup.addstr(idx+3,9,data[idx],curses.A_REVERSE)
                    popup.refresh()
            elif c == curses.KEY_PPAGE:
                i = data[idx][:1] 
                if i == 'H':
                    high = 65535
                elif i == 'R' or i == 'G' or i == 'B' or i == 'S':
                    high = 255
                elif i == 'T':
                    high = 500
                if value[idx] < high - 50:
                    value[idx] += 50
                    popup.addstr(idx+3,28,str(value[idx]) + '  ')
                    if i == 'R' or i == 'G' or i == 'B':
                        popup.addstr(7, 52, self.tohex(value[3],value[4],value[5]))
                    popup.refresh()
            elif c == curses.KEY_NPAGE:
                i = data[idx][:1] 
                if i == 'H' or i == 'S' or i == 'R' or i == 'G' or i == 'B':
                    low = 0
                elif i == 'T':
                    low = 153
                if value[idx] > low + 50:
                    value[idx] -= 50
                    popup.addstr(idx+3,28,str(value[idx]) + '  ')
                    if i == 'R' or i == 'G' or i == 'B':
                        popup.addstr(7, 52, self.tohex(value[3],value[4],value[5]))
                    popup.refresh()

            elif c == curses.KEY_LEFT:
                if self.light != None:
                    result = hub.set_light(self.light, 'on', True)
                else:  # it's a group
                    result = hub.set_group(self.group, 'on', True)
                popup.addstr(4,45,'ON', curses.A_REVERSE)
                popup.addstr(4,51,'OFF', curses.A_NORMAL)
                
            elif c == curses.KEY_RIGHT:
                if self.light != None:
                    result = hub.set_light(self.light, 'on', False)
                else:  # it's a group
                    result = hub.set_group(self.group, 'on', False)
                popup.addstr(4,45,'ON', curses.A_NORMAL)
                popup.addstr(4,51,'OFF', curses.A_REVERSE)

            elif curses.keyname(c) == '+':
                i = data[idx][:1] 
                if i == 'H':
                    high = 65535
                elif i == 'R' or i == 'G' or i == 'B' or i == 'S':
                    high = 255
                elif i == 'T':
                    high = 500
                if value[idx] < high:
                    value[idx] += 1
                    popup.addstr(idx+3,28,str(value[idx]) + '  ')
                    if i == 'R' or i == 'G' or i == 'B':
                        popup.addstr(7, 52, self.tohex(value[3],value[4],value[5]))
                    popup.refresh()
            elif curses.keyname(c) == '-':
                i = data[idx][:1] 
                if i == 'H' or i == 'S' or i == 'R' or i == 'G' or i == 'B':
                    low = 0
                elif i == 'T':
                    low = 153
                if value[idx] > low:
                    value[idx] -= 1
                    popup.addstr(idx+3,28,str(value[idx]) + '  ')
                    if i == 'R' or i == 'G' or i == 'B':
                        popup.addstr(7, 52, self.tohex(value[3],value[4],value[5]))
                    popup.refresh()
            elif curses.keyname(c) == 'w' or curses.keyname(c) == 'W':
                i = data[idx][:2]
                if i == 'Te':
                    cmd =  {'transitiontime' : 0, 'on' : True, 'ct' : value[idx]}
                elif i == 'Br':
                    cmd =  {'transitiontime' : 0, 'on' : True, 'bri' : value[idx]}
                elif i == 'Hu':
                    cmd =  {'transitiontime' : 0, 'on' : True, 'hue' : value[idx]}
                elif i == 'Sa':
                    cmd =  {'transitiontime' : 0, 'on' : True, 'sat' : value[idx]}
                elif i == 'Re' or i == 'Gr' or i == 'Bl':
                    xy = self.rgb2xy(value[3], value[4], value[5])
                    cmd =  {'transitiontime' : 0, 'on' : True, 'xy' : xy}
                    
                if self.light:
                    result = hub.set_light(self.light, cmd)
                elif self.group:
                    result = hub.set_group(self.group, cmd)
                popup.addstr(4,45,'ON', curses.A_REVERSE)
                popup.addstr(4,51,'OFF', curses.A_NORMAL)

                    
            elif curses.keyname(c) in "0123456789":
                i = data[idx][:1]
                if i == 'H':
                    high = 65535
                elif i == 'R' or i == 'G' or i == 'B' or i == 'S':
                    high = 255
                elif i == 'T':
                    high = 500

                value[idx] = high / 10 * int(curses.keyname(c))
                if i == 'T' and value[idx] < 153:
                    value[idx] = 153
                    
                popup.addstr(idx+3,28,str(value[idx]) + '   ')
                if i == 'R' or i == 'G' or i == 'B':
                    popup.addstr(7, 52, self.tohex(value[3],value[4],value[5]))
                popup.refresh()

            elif curses.keyname(c) == 'q' or curses.keyname(c) == 'Q':
                if self.light:
                    hub.set_light(self.light, 'on', False)
                elif self.group:
                    hub.set_group(self.group, 'on', False)
                break
        self.popup_destroy(scn, popup)
                

    
    # Get the initial configuration of the Bridge so we can see models of lights etc
    # self.bridge_config['lights']['1']['modelid']
    def list_bulbs(self, scn, hub):
        curses.curs_set(CURSOR_INVISIBLE)

        data = []
        data.append("{0:<4}{1:<9}{2:<19}{3:<23}{4}\n".format('ID', 'Modelid', 'Name' ,'ZigBee name', 'Manufacturer'))
        data.append("{0:=<78}".format('='))
        bridge_config = hub.get_api()
        lights = bridge_config['lights']
        for l in lights:
            data.append("{0:<4}{1:<9}{2:<19}{3:<23}{4}".format(l, lights[l]['modelid'], lights[l]['name'], \
                                                    lights[l]['type'], lights[l]['manufacturername']))

        data.append("\nPress 'q' to quit, arrow keys are active...")    
        
        self.showdata(scn, data)
        curses.curs_set(CURSOR_NORMAL)

#>>> b.get_group()
#{}
#>>> b.create_group('Sofa',[1,2])
#[{u'success': {u'id': u'1'}}]

#>>> b.get_group()
#{u'1': {u'action': {u'on': False, u'hue': 14910, u'colormode': u'ct', u'effect': u'none', u'alert': u'none', 
#u'xy': [0.4596, 0.4105], u'bri': 1, u'ct': 370, u'sat': 144}, u'lights': [u'1', u'2'], u'type': u'LightGroup', 
#u'name': u'Sofa'}}

#>>> b.get_group(1)
#{u'action': {u'on': False, u'hue': 14910, u'colormode': u'ct', u'effect': u'none', u'alert': u'none', u'xy': [0.4596, 0.4105], u'bri': 1, u'ct': 370, u'sat': 144}, u'lights': [u'1', u'2'], u'type': u'LightGroup', u'name': u'Sofa'}
#c['1']['lights']

    def list_groups(self, scn, hub):
        curses.curs_set(CURSOR_INVISIBLE)

        data = []
        lights = []
        data.append("{0:<4}{1:<25}{2}\n".format('ID', 'Name', 'Lights'))
        data.append("{0:=<78}".format('='))
        groups = hub.get_group()
        
        for g in groups:
            for l in groups[g]['lights']:   #dump unicode chars
                lights.append(int(l))
            data.append("{0:<4}{1:<25}{2}\n".format(g, groups[g]['name'], lights))
            lights = []
            
        data.append("\nPress 'q' to quit, arrow keys are active...")    
        
        self.showdata(scn, data)
        curses.curs_set(CURSOR_NORMAL)

    def create_group(self, scn, hub):
        title = 'Create new group'
        value = [0,0,0,0,0,0,0,0,0]
        data = ('Name of new group                :',\
                'Lights to add coma seperated     :')

        try:
            popup = curses.newwin(10, 78, 4, 2)            
            for i in range(len(data)):
                popup.addstr(i+3, 2, data[i])
                popup.addstr(7, 2, "Arrow Up/Down to select.")
                popup.addstr(8, 2, "Press 'w' to write to HUE,  'q' to exit.")
            popup.border('|','|','-','-','+','+','+','+')
            popup.addstr(0,7,'[ ')
            popup.addstr(0,9,title,curses.A_BOLD)
            popup.addstr(' ]')
            popup.nodelay(0)
            popup.keypad(1)
            curses.curs_set(0)
            popup.refresh()
        except:
            return

        name = ''
        lights = ''
        idx = 0
        popup.addstr(idx+3,2,data[idx],curses.A_REVERSE)
        popup.addstr(3,38, "Hit <Enter> to edit")
        popup.refresh()
        while True:
            c = popup.getch()

            if c == curses.KEY_DOWN:
                if idx + 1 < len(data):
                    popup.addstr(idx+3,2,data[idx],curses.A_NORMAL)
                    idx += 1
                    popup.addstr(idx+3,2,data[idx],curses.A_REVERSE)
                    popup.refresh()
            elif c == curses.KEY_UP:
                if idx -1 >= 0:
                    popup.addstr(idx+3,2,data[idx],curses.A_NORMAL)
                    idx -= 1
                    popup.addstr(idx+3,2,data[idx],curses.A_REVERSE)
                    popup.refresh()

            elif curses.keyname(c) == '^M':
                if idx == 0:
                    popup.addstr(3,38,"                           ")
                    popup.refresh()
                    curses.curs_set(CURSOR_NORMAL)
                    curses.echo()
                    name = popup.getstr(3,38)
                    popup.addstr(idx+3,2,data[idx],curses.A_NORMAL)
                    idx += 1
                    popup.addstr(idx+3,2,data[idx],curses.A_REVERSE)
                    popup.refresh()
                    lights = popup.getstr(4,38)
                    curses.curs_set(CURSOR_INVISIBLE)
                    curses.noecho()
                    curses.flushinp()
                    popup.addstr(idx+3,2,data[idx],curses.A_NORMAL)
                    idx -= 1
                    popup.addstr(idx+3,2,data[idx],curses.A_REVERSE)
                    popup.refresh()

                else:
                    popup.addstr(4,38,"                           ")
                    popup.refresh()
                    curses.curs_set(CURSOR_NORMAL)
                    curses.echo()
                    lights = popup.getstr(4,38)
                    curses.curs_set(CURSOR_INVISIBLE)
                
            elif curses.keyname(c) == 'w' or curses.keyname(c) == 'W':
                if name == '' or lights == '':
                    break
                else:
                    llist = []
                    for l in lights.split(','):
                        llist.append(int(l))
                    result = hub.create_group(name, llist)

                    if result[0].has_key('success'):
                        return
                    else:
                        self.popup_error(scn, "     Could not create group     ")
                        return
                        
            elif curses.keyname(c) == 'q' or curses.keyname(c) == 'Q':
                break
        self.popup_destroy(scn, popup)

    def delete_group(self, scn, hub):
        if hub != False:
            line = self.select_light_or_group(scn, hub, 'G')
            if line != None:
                group = int(line[0:2])
                if group == self.group:
                    self.group = None
                else:
                    hub.delete_group(group)

    def select_light_or_group(self, scn, hub, LorG):
        blank = "                                                                          "
        cl = []
        bridge_config = hub.get_api()
        if LorG == 'L':
            title = 'Light Bulb Selection'
            lights = bridge_config['lights']
            for l in lights:
                cl.append("{0:<4}{1:<9}{2:<19}{3:<23}{4}".format(l, lights[l]['modelid'], lights[l]['name'], \
                                                         lights[l]['type'], lights[l]['manufacturername']))
        elif LorG == 'G':
            title = 'Group Selection'
            lights = bridge_config['groups']
            for l in lights:
                cl.append("{0:<4}{1:<25}{2}".format(l, lights[l]['name'], lights[l]['lights']))
        else:
            return
        
        try:
            popup = curses.newwin(20, 78, 1, 2)

            # Fill in the first page
            for i in range(0,15):
                if i < len(cl):
                    popup.addstr(i+2, 3, cl[i])
                else:
                    break
            popup.addstr(18, 2, "<Enter> to select, 'q' quits")
            popup.border('|','|','-','-','+','+','+','+')
            popup.addstr(0,7,'[ ')
            popup.addstr(0,9,title,curses.A_BOLD)
            popup.addstr(' ]')
            popup.nodelay(0)
            popup.keypad(1)
            popup.scrollok(1)
            popup.idlok(1)            
            curses.curs_set(0)
            popup.refresh()
        except:
            pass
    
        #j = 0
        idx = 0
        page = 0
        popup.addstr(idx+2,3,cl[idx],curses.A_REVERSE)

        while True:
            c = popup.getch()

            if c == curses.KEY_DOWN:
                if idx == 14:
                    for j in range(2,17):
                        popup.addstr(j,3,blank)
                    idx = 0
                    page += 15
                    for i in range(0,15):
                        if idx+page < len(cl):
                            if idx == 0:
                                a = curses.A_REVERSE
                            else:
                                a = curses.A_NORMAL
                            popup.addstr(idx+2, 3, cl[idx+page], a)
                            idx += 1
                        else:
                            break
                    popup.move(2,3)
                    idx = 0
                    
                else:
                    if idx + page +1 < len(cl):
                        popup.addstr(idx+2,3,cl[idx+page],curses.A_NORMAL)
                        idx += 1
                        popup.addstr(idx+2,3,cl[idx+page],curses.A_REVERSE)
                        popup.refresh()
            elif c == curses.KEY_UP:
                if idx == 0:
                    idx = 14
                    page -= 15
                    if page < 0:
                        page = 0
                        idx = 0
                    else:
                        for j in range(2,17):
                            popup.addstr(j,3,blank)
                        for i in range(0,15):
                            if idx+page >= 0:
                                if idx == 14:
                                    a = curses.A_REVERSE
                                else:
                                    a = curses.A_NORMAL
                                popup.addstr(idx+2, 3, cl[idx+page], a)
                                idx -= 1
                            else:
                                break
                        popup.move(16,3)
                        idx = 14
                    
                else:
                    if idx + page > 0:
                        popup.addstr(idx+2,3,cl[idx+page],curses.A_NORMAL)
                        idx -= 1
                        popup.addstr(idx+2,3,cl[idx+page],curses.A_REVERSE)
                        popup.refresh()

            elif curses.keyname(c) == '^M':
                light = popup.instr(idx+2,3,74)
                scn.touchwin()
                scn.refresh()
                curses.curs_set(1)
                return light
    
            elif curses.keyname(c) == 'q':
                scn.touchwin()
                scn.refresh()
                curses.curs_set(1)
                return None


    def popup_error(self, scn, text):
        width = len(text) + 4
        try:
            popup = curses.newwin(6, width, 10, 10)
            x = (width - len(text)) / 2
            popup.addstr(2, x, text)
            popup.addstr(3, 8, "Hit <ENTER> to return...")
            popup.border('|','|','-','-','+','+','+','+')
            popup.nodelay(0)
            curses.curs_set(CURSOR_INVISIBLE)
            popup.refresh()
        except:
            pass
        c = popup.getch()
        curses.curs_set(CURSOR_NORMAL)
        scn.touchwin()
        scn.refresh()
        return curses.keyname(c)

    def popup_colour_dialog(self, scn, hub, cl, title):
        try:
            popup = curses.newwin(20, 64, 4, 8)            
            for i in range(len(cl)):
                popup.addstr(i+3, 9, cl[i])
                popup.addstr(14, 2, "Arrow Up/Down to select. Left/Right to turn on/off.")
                popup.addstr(15, 2, "Page Up/Page Down or + and - to change values.")
                popup.addstr(16, 2, "0 to 9 jump to itermediate values - great for hue.")
                popup.addstr(17, 2, "Press 'w' to write to HUE,  'q' to exit.")
            popup.border('|','|','-','-','+','+','+','+')
            popup.addstr(0,7,'[ ')
            popup.addstr(0,9,title,curses.A_BOLD)
            popup.addstr(' ]')
            popup.nodelay(0)
            popup.keypad(1)
            curses.curs_set(0)
            popup.refresh()
        except:
            pass
    
        return popup
            
    def popup_destroy(self, scn, popup):
        popup.erase()
        popup.refresh()
        scn.erase()
        scn.touchwin()
        scn.refresh()
        curses.curs_set(1)

        
    def popup_menu(self, scn):
        cmds = 'aAdDgGnNcClLoOqQrRsS'
        c = 0
        text = """
                    
                  
    Authenticate system with Bridge....................A 
    Select light to use................................S 
    Select group to use................................O 
    Add new bulb to Bridge.............................N
    Adjust colours | toggle light on/off...............C
    List bulbs connected to Bridge.....................L
    List groups configured in Bridge...................G
    Create new group...................................R
    Delete group.......................................D
    Exit Huecmdr.......................................Q
        
    Press command key, can be upper or lower case. [   ]

    Currently Selected:  Light [      ] - Group [      ]
    Bridge IP Address :  
        """

        try:
            popup = curses.newwin(21, 64, 2, 6)
            popup.addstr(1, 1, text)
            popup.border('|','|','-','-','+','+','+','+')
            popup.addstr(0,7,'[ ')
            popup.addstr(0,9,"Huecmdr Command Summary",curses.A_BOLD)
            popup.addstr(' ]')
            popup.nodelay(0)
            curses.curs_set(CURSOR_INVISIBLE)
            popup.refresh()
        except:
            pass

        if self.light == None:
            popup.addstr(17,33,str(self.light))
        else:
            popup.addstr(17,34,"{0:0>2}".format(self.light))
        
        if self.group == None:
            popup.addstr(17,50,str(self.group))
        else:
            popup.addstr(17,51,"{0:0>2}".format(self.group))

        popup.addstr(18,25,"[ {0} ]".format(self.ip))
        popup.move(15,53)
        popup.refresh()

        while curses.keyname(c) not in cmds:
            c = popup.getch()
            popup.addstr(15,53, curses.keyname(c))
            popup.refresh()
            time.sleep(.2)
            popup.addstr(14,53, '  ')
        curses.curs_set(CURSOR_NORMAL)
        scn.touchwin()
        scn.refresh()
        scn.erase()
        return curses.keyname(c)

    def show_intro(self, scn):
        # create with the figlet command
        text = """
          Welcome to:

           _   _                               _      
          | | | |_   _  ___  ___ _ __ ___   __| |_ __ 
          | |_| | | | |/ _ \/ __| '_ ` _ \ / _` | '__|
          |  _  | |_| |  __/ (__| | | | | | (_| | |   
          |_| |_|\__,_|\___|\___|_| |_| |_|\__,_|_|   
                                            
          """

        scn.erase()
        scn.addstr(2, 2, text)
        scn.addstr(12,27, VERSION)
        scn.addstr(13,27, VERSION_DATE)
        scn.addstr(14,27,"By George Farris - farrisga@gmail.com")
        scn.addstr(18,10, "A Phillips HUE test utility for Linux...")
        scn.addstr(20,10, "Any key to continue...")
        scn.refresh()
        scn.nodelay(0)
        scn.getch()
    
    def main(self, scr, term):
        scn = self.setup_screen()

        dateString = ''
        self.firstChar = True
        today = datetime.datetime.today()
    
        curses.curs_set(CURSOR_INVISIBLE)
        self.show_intro(scn)
        curses.curs_set(CURSOR_NORMAL)
        scn.erase()

        config_file = os.path.join(os.getenv('HOME'), '.python_hue')
        
        try:
            f = open(config_file, 'r')
            config = json.loads(f.read())
            if self.ip is None:
                self.ip = list(config.keys())[0]
            if self.username is None:
                self.username = config[self.ip]['username']
            # Connect to the Bridge
            hub = Bridge(self.ip) 
        except:
            hub = self.authenticate(scn)
        
        while (True):
            c = self.popup_menu(scn)
            
            if c == 'q' or c == 'Q':
                term.terminate()
            elif c == 'a' or c == 'A':
                self.authenticate(scn)
            elif c == 's' or c == 'S':
                if hub != False:
                    line = self.select_light_or_group(scn, hub, 'L')
                    if line != None:
                        self.light = int(line[0:2])
                        self.group = None
            elif c == 'o' or c == 'O':
                if hub != False:
                    line = self.select_light_or_group(scn, hub, 'G')
                    if line != None:
                        self.group = int(line[0:2])
                        self.light = None
            elif c == 'n' or c == 'N':
                if hub != False:
                    self.add_new_bulb(scn, hub)
            elif c == 'c' or c == 'C':
                if hub != False:
                    self.adjust_colours(scn, hub)
            elif c == 'l' or c == 'L':
                if hub != False:
                    self.list_bulbs(scn, hub)
            elif c == 'g' or c == 'G':
                if hub != False:
                    self.list_groups(scn, hub)
            elif c == 'r' or c == 'R':
                if hub != False:
                    self.create_group(scn, hub)
            elif c == 'd' or c == 'D':
                if hub != False:
                    self.delete_group(scn, hub)


                
if __name__ == "__main__":
    hue = Hue()
    curses.wrapper(hue.main, hue)

