#from instances import *
import os

INSTANCES_DIR = './instances'


if __name__ == "__main__":
    print 'Pytomation'
    scripts = os.listdir(INSTANCES_DIR)
    for script_name in scripts:
        print "Found Instance Script: " + script_name
        stuff = __import__("instances.%s" % script_name)
#    try:
#        my_module = __import__("myapp.%s" % script_name, fromlist=["list"])
#    except ImportError:
#        pass

