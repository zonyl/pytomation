"""
File:
    config.py

Description:

This is the main configuration file for Pytomation.  It is divided into
sections.  The first section is strictly system configuration, it 
should not generally be changed unless you are doing driver or system
code.



License:
    This free software is licensed under the terms of the GNU public 
    license, Version 3.

System Versions and changes:
    Initial version created on Nov 11, 2012
    2012/11/11 - 1.0 - Global debug dictionary created
    2012/11/18 - 1.1 - Log file pieces added
    
"""
import os
import sys

# ********************* SYSYTEM CONFIGURATION ONLY ********************

# debug{} holds the global debug dictionary. A completel description is 
# availble in Pytomation documentation.  Briefly it holds a string key
# and an integer value.  Example: ['Serial':1, 'UPB':0]  These values
# are set and registered with each module in the class __init__().
# 
# Only system values are initialized here.
debug = {'HAInterface':0, 'Serial':0}




# ********************* USER CONFIGURATION ****************************

# LOGGING
# Setup logging of Pytomation to a log file.  Pytomation will rotate
# the log file out to pylog_date_time.log every time it starts, if  
# "logfilePreserve" and "logging" is set to "True".  If you want to 
# turn log file logging off, just set "logging" to "False"
# Logfiles can be rotated on a weekly or monthly basis by setting
# "logfileRotate to 'week' or 'month'
# If logfileTimestamp is set to a format that can be used by the Python
# time.strftime() function like the example below that will be printed at
# the beginning of each debug line.  Otherwise it should be an empty
# string "".
# logfileTimestamp = "[%Y/%M/%D-%H:%M:%S]"

logfile = os.path.join(sys.path[0], 'pylog.log')
logfilePreserve = True
logfileTimestamp = "[%Y/%m/%d %H:%M:%S] "
#logfileTimestamp = ""
logfileRotate = 'week'
logging = True
