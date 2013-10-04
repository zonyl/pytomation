# Pytomation

---

Pytomation is an extensible automation system written in Python. It's uses 
include home automation and lighting control but is certainly not limited to 
that.

#### Supported
Pytomation currently has support for the following hardware interfaces with 
more planned in the future.

   - [Insteon](http://www.insteon.com/) / X10 (2412N, 2412S)
   - UPB (Universal Powerline Bus) (Serial PIM)
   - [JDS Stargate](http://www.jdstechnologies.com/stargate.html) (RS232 / RS485)
   - [Weeder](http://www.weedtech.com/) Digital I/O board (Wtdio/RS232)
   - W800RF32 X10 RF receiver (W800/RS232)
   - [Arduino](http://www.arduino.cc) Uno board (USB)
   - X10 CM11a (RS232)
   - Mochad X10 CM15 (USB) and CM19 (USB)
   - [Misterhouse](http://misterhouse.sourceforge.net/) Voice Commands MHSend (TCP)

### Future
   - Z-Wave (Aeon Labs) DSA02203-ZWUS
   - Weeder Analog I/O board (Wtaio/RS232)

---

###INSTALLATION


#### DEPENDENCIES
Before you can create an instance and run Pytomation automation software you must satisfy a few dependencies. Pytomation is written in Python and currently has been tested under versions 2.6.x and 2.7.x.
Pytomation also requires the following packages to be installed: 
 - Pyserial - Support for RS232 serial interfaces. - Pyephem - High-precision astronomy computations for sunrise/sunset. - Pytz - World timezone definitions. - Mock - Python testing library. - Git - Version control software. - Debian packages are available for Pyserial and can be installed with : 
     
       sudo apt-get install python-serial 
or search for python serial in your software manager.

The other pieces can be installed with ""pip". "Pip" is a tool for installing and managing Python packages, such as those found in the Python Package Index.
Again, under Debian distributions you can install the python-pip package: 
     sudo apt-get install python-pip
     Once pip is installed it is easy to install the rest of the dependencies with the following commands.
    sudo pip install pytz pyephem mock git
    ####INSTALL
You are now ready to install pytomation. Change into the directory that Pytomation resides in from the git clone command above and run "./install.sh". You may have to make it executable with the command chmod +x ./install.sh first. Install.sh can take an optional argument which points to an alternate installation directory:     ./install.sh /some/other/folder/pytomation
     The install.sh command does the following: 
  - Confirms where you are installing Pytomation to.  - Makes a "pyto" user and creates the home directory.  - Copies all the necessary files into Pytomations HOME.  - Creates a /usr/bin/pytomation.sh command to start Pytomation.  - Creates an /etc/init.d/pyto script for starting Pytomation on boot.You are now ready to configure pytomation and create an instance for your devices.
