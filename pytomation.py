import os
from pytomation.common import config, pytomation_system

INSTANCES_DIR = './instances'


if __name__ == "__main__":
    print 'Pytomation'
    scripts = []
    script_names = os.listdir(INSTANCES_DIR)
    for script_name in script_names:
        if script_name.lower()[-3:]==".py" and script_name.lower() != "__init__.py":
            try:
                module = "instances.%s" % script_name[0:len(script_name)-3]
                print "Found Instance Script: " + module
                scripts.append( __import__(module, fromlist=['instances']))
            except ImportError, ex:
                print 'Error' + str(ex)
    print "Total Scripts: " + str(len(scripts))

    if len(scripts) > 0:
        # Start the whole system.  pytomation.common.system.start()
        try:
            loop_action=scripts[0].MainLoop
        except AttributeError, ex:
            loop_action=None

        pytomation_system.start(
            loop_action=loop_action,
            loop_time=config.loop_time, # Loop every 1 sec
            admin_user=config.admin_user,
            admin_password=config.admin_password,
            telnet_port=config.telnet_port,
            http_address=config.http_address,
            http_port=config.http_port,
            http_path=config.http_path,
        )
    else:
        print "No Scripts found. Exiting"
