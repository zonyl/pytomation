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
    
"""

# ********************* SYSYTEM CONFIGURATION ONLY ********************

# debug{} holds the global debug dictionary. A completel description is 
# availble in Pytomation documentation.  Briefly it holds a string key
# and an integer value.  Example: ['Serial':1, 'UPB':0]  These values
# are set and registered with each module in the class __init__().
# 
# Only system values are initialized here.
debug = {'HAInterface':0, 'Serial':0}




# ********************* USER CONFIGURATION ****************************

