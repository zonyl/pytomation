#from instances import *
import os

INSTANCES_DIR = './instances'


if __name__ == "__main__":
    print 'Pytomation'
    scripts = os.listdir(INSTANCES_DIR)
    for script_name in scripts:
	if script_name.lower()[-3:]==".py" and script_name.lower() != "__init__.py":
	        print "Found Instance Script: " + script_name
        	stuff = __import__("instances.%s" % script_name)
#    try:
#        my_module = __import__("myapp.%s" % script_name, fromlist=["list"])
#    except ImportError:
#        pass

