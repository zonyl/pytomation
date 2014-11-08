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
   - [Venstar ColorTouch](http://www.venstar.com/Thermostats/ColorTouch/) Venstar ColorTouch Thermostat (5/6800)
   - [Weeder](http://www.weedtech.com/) Digital I/O board (Wtdio/RS232)
   - [Logitech Harmony](http://www.myharmony.com) Universal WiFi Remote (Harmony Ultimate)
   - [WGL Designs](http://wgldesigns.com/w800.html) W800RF32 X10 RF receiver (W800/RS232)
   - [Arduino](http://www.arduino.cc) Uno board (USB)
   - [X10](http://x10pro-usa.com/x10-home/controllers/wired-controllers/cm11a.html) CM11a (RS232)
   - Mochad X10 CM15 (USB) and CM19 (USB)
   - [Misterhouse](http://misterhouse.sourceforge.net/) Voice Commands MHSend (TCP)
   - [Spark I/O](http://www.spark.io) WiFi devices
   - Z-Wave (Aeon Labs via pyOpenzwave) DSA02203-ZWUS 

### Future
   - Weeder Analog I/O board (Wtaio/RS232)
   - Ube Wifi Devices
   - CoralStar WiFi Devices

---

###INSTALLATION


#### DEPENDENCIES

Before you can create an instance and run Pytomation automation software you must satisfy a few dependencies. Pytomation is written in Python and currently has been tested under versions 2.6.x and 2.7.x. 

Pytomation also requires the following packages to be installed for normal operation:
 
 - pySerial - Support for RS232 serial interfaces.
 - Pyephem - High-precision astronomy computations for sunrise/sunset.
 - Pytz - World timezone definitions.

Additional packages are required for development and testing. See `requirements.txt` for a more complete list.

Debian packages are available for pySerial and pytz. They can be installed with : 

    sudo apt-get install git python-serial python-tz

For other operating systems, search your package manager for the equivalent packages or use pip to install the Python dependencies.

The remaining dependencies can be installed with `pip`. Pip is a tool for installing and managing Python packages, such as those found in the Python Package Index.

Again, under Debian distributions you can install the python-pip package: 

    sudo apt-get install python-pip

Once pip is installed it is easy to install the rest of the dependencies with the following commands.

    sudo pip install pyephem

    
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

