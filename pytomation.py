import os
from pytomation.common import config, system

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

    # Start the whole system.  pytomation.common.system.start()
    system.start(
        loop_action=scripts[0].MainLoop if scripts[0].MainLoop else None,
        loop_time=config.loop_time, # Loop every 1 sec
        admin_user=config.admin_user,
        admin_password=config.admin_password,
        telnet_port=config.telnet_port,
        http_address=config.http_address,
        http_port=config.http_port,
        http_path=config.http_path,
    )
