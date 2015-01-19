# Pytomation

---

Pytomation is an extensible device communication and automation system written in Python. It's uses 
include home automation and lighting control but is certainly not limited to 
that.  It is supported on any platform that support Python ( Windows, Mac OS-X, Linux, etc )

#### Supported
Pytomation currently has support for the following hardware interfaces with 
more planned in the future.

   - [Insteon](http://www.insteon.com/) / X10 (2412N, 2412S, 2413U)
   - [UPB](http://www.pulseworx.com/products/products_.htm) Universal Powerline Bus (Serial PIM)
   - [Belkin WeMo](http://www.belkin.com/us/Products/home-automation/c/wemo-home-automation)  WeMo Wifi Switches 
   - [JDS Stargate](http://www.jdstechnologies.com/stargate.html) (RS232 / RS485)
   - [Radio Thermostat](http://www.radiothermostat.com/ ) WiFi Enabled Thermostat (CT30)
   - [Nest Labs](https://nest.com/) Nest thermostat
   - [Venstar ColorTouch](http://www.venstar.com/Thermostats/ColorTouch/) Thermostat (5/6800)
   - [Weeder](http://www.weedtech.com/) Digital I/O board (Wtdio/RS232)
   - [Logitech Harmony](http://www.myharmony.com) Universal WiFi Remote (Harmony Ultimate)
   - [WGL Designs](http://wgldesigns.com/w800.html) W800RF32 X10 RF receiver (W800/RS232)
   - [Arduino](http://www.arduino.cc) Uno board (USB)
   - [X10](http://x10pro-usa.com/x10-home/controllers/wired-controllers/cm11a.html) CM11a (RS232)
   - Mochad X10 CM15 (USB) and CM19 (USB)
   - [Misterhouse](http://misterhouse.sourceforge.net/) Voice Commands MHSend (TCP)
   - [Spark I/O](http://www.spark.io) WiFi devices
   - Z-Wave (Aeon Labs via python-Openzwave) DSA02203-ZWUS 

### Future
   - Weeder Analog I/O board (Wtaio/RS232)
   - Ube Wifi Devices
   - CoralStar WiFi Devices

### FEATURES
   - Written in Python
   - REST API
   - Mobile Web and Android clients w/ continuous device state updates (web-sockets)
   - Voice Commands from Android (“Home Control” app)
   - Local Telnet and Web access
   - Unique language to describe devices and actions
   - Smart objects: Doors, Lights, Motion, Photocell etc.
   - Optional “Mainloop” programming, for more complicated control
   - Optional “Event driven” programming, for complex actions when a device state changes
   - Time of day on and off control
   - Delays for time off
   - Idle command, device will return to "idle" state
   - Map one command to another with optional source and time
   - Good hardware support with more coming
   - Very easy to add new hardware drivers
   - Good documentation complete with examples
   - Much more

---

###INSTALLATION


#### DEPENDENCIES

Before you can create an instance and run Pytomation automation software you must satisfy a few dependencies. Pytomation is written in Python and currently has been tested under versions 2.6.x and 2.7.x. 

Pytomation also requires the following packages to be installed for normal operation:
 
 - pySerial - Support for RS232 serial interfaces.
 - Pyephem - High-precision astronomy computations for sunrise/sunset.
 - Pytz - World timezone definitions.

Optional Packages:
 - python-gevent - A coroutine-based Python networking library (PytoWebSocketServer)
 - python-openssl - Allows the PytoWebSocketServer to use native SSL (https and wss connections)

Additional packages are required for development and testing. See `requirements.txt` for a more complete list.

Debian packages are available for pySerial, pytz, pythone-gevent, and python-openssl. They can be installed with : 

    sudo apt-get install git python-serial python-tz python-gevent python-openssl

For other operating systems, search your package manager for the equivalent packages or use pip to install the Python dependencies.

The remaining dependencies can be installed with `pip`. Pip is a tool for installing and managing Python packages, such as those found in the Python Package Index.

Again, under Debian distributions you can install the python-pip package: 

    sudo apt-get install python-pip

Once pip is installed it is easy to install the rest of the dependencies with the following commands:

    sudo pip install pyephem

To use the optional websocket server:

    sudo pip install gevent-websocket

The gevent-websocket server is pretty fast, but can be accelerated further by installing wsaccel and ujson or simplejson

    sudo pip install wsaccel ujson


Build openzwave and python-openzwave
====================================
Aeon Labs Z-Wave requires python-openzwave, which  must be compiled from source. The instructions below list how to build from the development repositories. There is also prepared source avaiable at http://bibi21000.no-ip.biz/python-openzwave/python-openzwave-0.2.6.tgz, but that didn't work for me.

The following was extracted and adapted from the python-openzwave INSTALL_MAN.txt:

    sudo apt-get install mercurial subversion python-pip python-dev python-setuptools python-louie python-sphinx make build-essential libudev-dev g++
    sudo pip install cython==0.14
    sudo pip install sphinxcontrib-blockdiag sphinxcontrib-actdiag
    sudo pip install sphinxcontrib-nwdiag sphinxcontrib-seqdiag

    hg clone https://code.google.com/p/python-openzwave/
    cd python-openzwave
    svn checkout http://open-zwave.googlecode.com/svn/trunk/ openzwave

#### Method 1 (Install Everything via Scripts)

    ./compile.sh
    sudo ./install.sh

#### Method 2 (Install Manually)
If you installed everthing, stop here. Otherwise, go to the openzwave directory and build it:

    cd openzwave/cpp/build
    make
    cd ../../..

Build python-openzwave:

    python setup-lib.py build
    python setup-api.py build

And install them:

    sudo python setup-lib.py install
    sudo python setup-api.py install

#### Permissions
Like with all other interfaces. Make sure the pyto user account owns or otherwise has permissions to use the device. You may want to give your own usr account access as well.

    sudo chown youruseraccount:pyto /dev/yourzwavestick
    sudo chmod 770 /dev/yourzwavestick

or

    sudo chown pyto:pyto /dev/yourzwavestick
    sudo chmod 770 /dev/yourzwavestick

#### ozwsh (OpenZWave Shell, for testing)

    sudo pip install urwid louie
    /ozwsh.sh --device=/dev/yourzwavestick

####INSTALL

You are now ready to install pytomation. First, clone the pytomation git repository. Change into the pytomation repo directory and run `./install.sh`. You may have to make it executable with the command `chmod +x ./install.sh` first. Install.sh can take an optional argument which points to an alternate installation directory:

     ./install.sh /some/other/folder/pytomation

The install.sh command does the following:
 
  - Confirms where you are installing Pytomation to.
  - Makes a "pyto" user and creates the home directory.
  - Copies all the necessary files into Pytomations HOME.
  - Creates an /etc/init.d/pytomation init script for starting Pytomation on boot.
  - Configures pytomation to start automatically at boot time

You are now ready to configure pytomation and create an instance for your devices.

