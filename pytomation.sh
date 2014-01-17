#!/bin/bash

# Redirect stdout ( > ) into a named pipe ( >() ) running "tee"
exec >> /var/log/pyto.log
exec 2>&1

# It's possible PYHOME in /usr/bin has been changed by the install.sh script
PYHOME="/home/pytomation"
cd $PYHOME
PROGRAM='python ./pytomation.py'

# Put a flag into the logs so we can find when pytomation was restarted
echo "=========RESTART==========" >> ./pylog.log
echo "=========RESTART=========="

$PROGRAM &
PID=$!
if [ -w /var/run ]; then
    echo $PID > /var/run/pytomation.pid
else
    echo "Running as regular user can't write PID file to /var/run/pytomation.pid..."
    echo "PID is $PID..."
fi
