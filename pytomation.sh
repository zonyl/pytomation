#!/bin/sh
PROGRAM='python ./pytomation.py'
$PROGRAM &
PID=$!
echo $PID > /var/run/pytomation.pid
