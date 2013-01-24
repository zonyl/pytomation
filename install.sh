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

echo "Setting install location in pytomation.sh"
echo "#!/bin/bash" > /usr/bin/pytomation.sh
echo "PYHOME=\"/home/pytomation\""  >> /usr/bin/pytomation.sh
echo "cd \$PYHOME"   >> /usr/bin/pytomation.sh
echo "PROGRAM='python ./pytomation.py'"  >> /usr/bin/pytomation.sh
echo "\$PROGRAM &"  >> /usr/bin/pytomation.sh
echo "PID=\$!"  >> /usr/bin/pytomation.sh
echo "if [ -w /var/run ]; then"  >> /usr/bin/pytomation.sh
echo "    echo \$PID > /var/run/pytomation.pid"  >> /usr/bin/pytomation.sh
echo "else"  >> /usr/bin/pytomation.sh
echo "    echo \"Running as regular user can't write PID file to /var/run/pytomation.pid...\""  >> /usr/bin/pytomation.sh
echo "    echo \"PID is \$PID...\""  >> /usr/bin/pytomation.sh
echo "fi"  >> /usr/bin/pytomation.sh

echo "Copying init script to /etc/init.d..."
cp pyto /etc/init.d

echo "Making sure scripts are excutable..."
chmod +x /usr/bin/pytomation.sh
chmod +x /etc/init.d/pyto

echo "Setting Pytomation to start from run level 2"
ln -s ../init.d/pyto /etc/rc2.d/S99pyto

echo "Finished..."
