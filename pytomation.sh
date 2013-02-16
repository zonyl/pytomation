#!/bin/bash 

# It's possible PYHOME in /usr/bin has been changed by the install.sh script
PYHOME="/home/george/Projects/pytomation"
cd $PYHOME
PROGRAM='python ./pytomation.py'
$PROGRAM &
PID=$!
if [ -w /var/run ]; then
    echo $PID > /var/run/pytomation.pid
else
    echo "Running as regular user can't write PID file to /var/run/pytomation.pid..."
    echo "PID is $PID..."
	echo $PID > pytomation.pid
fi
