#!/bin/bash
echo
echo
if [ $UID != 0 ]; then
    echo "You must run this with the sudo command or as root..."
    exit
fi

# Set a default home
PYHOME="/home/pytomation"

if [ "x$1" == "x" ]; then
    echo "You are using the default install location..."
    echo "You can change this by running install.sh with an path..."
    echo "Example:  install.sh /usr/local/lib/pytomation"
fi

echo -n "Install location is -> $PYHOME [Y/n] ?"
read a
if [ "x$a" == "xn" ] || [ "x$a" == "xN" ]; then
    exit
fi

echo "Creating user pyto..."
useradd -m -d $PYHOME pyto
if [ ! -d $PYHOME ]; then
    mkdir $PYHOME
fi

echo "Copying files to $PYHOME..."
cp -a * $PYHOME
chown -R pyto $PYHOME

OLD_INIT_SCRIPT="/etc/init.d/pyto"
NEW_INIT_SCRIPT="/etc/init.d/pytomation"
if [ -e "$OLD_INIT_SCRIPT" ]; then
    echo "Removing old init script at $OLD_INIT_SCRIPT ..."
    rm "$OLD_INIT_SCRIPT"
fi

echo "Copying init script to /etc/init.d..."
cp pytomation.init "$NEW_INIT_SCRIPT"

echo "Making sure scripts are excutable..."
chmod +x "$NEW_INIT_SCRIPT"

# Old versions of the install script created a manual rcS symlink for runlevel
# 2 only, which is not correct. Force remove any old symlinks that might exist
# before using update-rc.d to create the proper entries (start or kill) at all
# runlevels.
echo "Removing old rcS entries ..."
update-rc.d -f pyto remove

echo "Configuration Pytomation to run at boot ..."
update-rc.d pytomation defaults

echo "Finished..."
