"""
File:
    config.py

Description:

This is the main configuration file for Pytomation.  It is divided into
sections each pertaining to a specific part of the system.  These sections 
cannot be deleted, the variables can be modified but they must have a value.


License:
    This free software is licensed under the terms of the GNU public 
    license, Version 3.

System Versions and changes:
    Initial version created on Nov 11, 2012
    2012/11/11 - 1.0 - Global debug dictionary created
    2012/11/18 - 1.1 - Log file pieces added
    2013/01/24 - 1.2 - New logging system and start loop vars
        
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
telnet_port = None
loop_time = 1


# ********************* LOGGING CONFIGURATION ****************************
"""
# LOGGING
 Setup logging of Pytomation to a log file.  Pytomation uses the standard
 Python logging modules which supports a wide variety of functions from
 log rotation to logging to a remote system.

 Please see http://docs.python.org/2/library/logging.html for full information.
 
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
                   #"Light": "DEBUG",
                   }

# Logging file path
logging_file = os.path.join(sys.path[0], 'pylog.log')

# Logging entry message format
logging_format = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'

# Logging entry date format
logging_datefmt = "%Y/%m/%d %H:%M:%S"

#*************  NOTE ********************************
# Log rotation is currently not working, we will update this section when 
# it changes but for now please leave it set to "None"
#
#logging_rotate_when = 'midnight' # s, m, h, d, w (interval 0=Monday), midnight, None
logging_rotate_when = None # s, m, h, d, w (interval 0=Monday), midnight, None
logging_rotate_interval = 1
logging_rotate_backup = 4

