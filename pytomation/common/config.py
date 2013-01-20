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

#
#********************* SYSYTEM CONFIGURATION ONLY ********************
#
admin_user = 'pyto'
admin_password = 'mation'
http_address = "127.0.0.1"
http_port = 8080
http_path = "./pytomation_web"
telnet_port = 2000
loop_time = 1


# ********************* USER CONFIGURATION ****************************
"""
# LOGGING
 Setup logging of Pytomation to a log file.  Pytomation will rotate
 the log file out to pylog_date_time.log every time it starts, if  
 "logfilePreserve" and "logging" is set to "True".  If you want to 
 turn log file logging off, just set "logging" to "False"
 Logfiles can be rotated on a weekly or monthly basis by setting
 "logfileRotate to 'week' or 'month'
 If logfileTimestamp is set to a format that can be used by the Python
 time.strftime() function like the example below that will be printed at
 the beginning of each debug line.  Otherwise it should be an empty
 string "".
 logfileTimestamp = "[%Y/%M/%D-%H:%M:%S]"

 Logging Levels:

 DEBUG | INFO | WARNING | ERROR | CRITICAL
"""

## Default logging level
logging_default_level = "INFO"

# Logging modules is dict() of modules names and their minimum logging
# levels.  If it is not listed default level is used
#
logging_modules = {
                   'LoggingTests': "CRITICAL",
                   #'Stargate': 'DEBUG',
                   #'InsteonPLM': 'DEBUG',
                   #'W800rf32': 'DEBUG',
                   #'Wtdio': 'DEBUG',
                   #'UPB': 'DEBUG',
                   }

# Logging file path
logging_file = os.path.join(sys.path[0], 'pylog.log')

# Logging entry message format
logging_format = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'

# Logging entry date format
logging_datefmt = "%Y/%m/%d %H:%M:%S"

#logfileRotate = 'week'
