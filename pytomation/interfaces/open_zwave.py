"""
Initial Openzwave support (with Aeon Labs z-stick S2)

by texnofobix@gmail.com

Currently only controls switches and dimmers
"""

#from .common import *
from .ha_interface import HAInterface

import time
try:
    from openzwave.option import ZWaveOption
    from openzwave.network import ZWaveNetwork
    #from openzwave.node import ZWaveNode
    from louie import dispatcher, All
except:
    print ("Error importing Openzwave and/or Python-Openzwave")


class Open_zwave(HAInterface):
    VERSION = '0.0.2'
    awake = False
    ready = False
    nodesdisplayed = False

    def louie_network_ready(self, network):
        self._logger.info(">>>>>>> Hello from network : I'm ready : %d nodes were found." % self._network.nodes_count)     
        self._logger.info(">>>>>>> Hello from network : my controller is : %s" % self._network.controller)
        dispatcher.connect(self.louie_node_update, ZWaveNetwork.SIGNAL_NODE)
        dispatcher.connect(self.louie_value_update, ZWaveNetwork.SIGNAL_VALUE)

    def louie_node_update(self, network, node):
        self._logger.info('>>>>>>> Hello from node : %s.' % node)

    def louie_value_update(self, network, node, value):
        self._logger.info('>>>>>>> Hello from value : %s.' % value)

    def __init__(self, *args, **kwargs):
        self._serialDevicePath = kwargs.get('serialDevicePath', None)
        self._options = ZWaveOption(self._serialDevicePath, \
          config_path=kwargs.get('config_path', "/etc/openzwave/"), \
          user_path=".", cmd_line="")
        self._options.set_log_file("OZW_Log.log")
        self._options.set_append_log_file(False)
        self._options.set_console_output(False)
        #self._options.set_save_log_level(log)
        self._options.set_save_log_level('Info')
        self._options.set_logging(True)
        self._options.set_notify_transactions(True)
        self._options.lock()

        self._network = ZWaveNetwork(self._options, log=None,autostart=False)
        dispatcher.connect(self.louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)
        self._network.start()
        super(Open_zwave, self).__init__(self, *args, **kwargs)

    def _printNetwork(self, node):
        print
        print "------------------------------------------------------"
        print "%s - Name : %s" % (self._network.nodes[node].node_id,
            self._network.nodes[node].name)
        print "%s - Manufacturer name / id : %s / %s" % (
            self._network.nodes[node].node_id,
            self._network.nodes[node].manufacturer_name,
            self._network.nodes[node].manufacturer_id)
        print "%s - Product name / id / type : %s / %s / %s" % (
            self._network.nodes[node].node_id,
            self._network.nodes[node].product_name,
            self._network.nodes[node].product_id,
            self._network.nodes[node].product_type)
        print "%s - Version : %s" % (self._network.nodes[node].node_id,
            self._network.nodes[node].version)
        print "%s - Command classes : %s" % (self._network.nodes[node].node_id,
            self._network.nodes[node].command_classes_as_string)
        print "%s - Capabilities : %s" % (self._network.nodes[node].node_id,
            self._network.nodes[node].capabilities)
        print "%s - Neighbors : %s" % (self._network.nodes[node].node_id,
            self._network.nodes[node].neighbors)
        print "%s - Can sleep : %s" % (self._network.nodes[node].node_id,
            self._network.nodes[node].can_wake_up())

    def _init(self, *args, **kwargs):
        super(Open_zwave, self)._init(self, *args, **kwargs)

    def _readInterface(self, lastPacketHash):
        if (self._network.state >= self._network.STATE_AWAKED
            and not self.awake):
            self.awake = True
            self._logger.info("Network Awaked")
        if (self._network.state >= self._network.STATE_READY
            and not self.ready):
            self.ready = True
            self._logger.info("Network Ready")
        if not self.awake:
            time.sleep(1.0)
            self._logger.debug("Not awaked")
            return
        if self.awake and not self.ready:
            time.sleep(1.0)
            self._logger.debug("Not ready")
            return
        if not self.nodesdisplayed and self.ready:
            for node in self._network.nodes:
                self._printNetwork(node)
            self.nodesdisplayed = True
        time.sleep(1)

    def version(self):
        self._logger.info("Open_zwave Pytomation Driver version " +
                          self.VERSION)
        self._logger.info("Use openzwave library : %s" %
                          self._network.controller.ozw_library_version)
        self._logger.info("Use python library : %s" %
                          self._network.controller.python_library_version)
        self._logger.info("Use ZWave library : %s" %
                          self._network.controller.library_description)

    def on(self, address):
        node = int(address)
        for val in self._network.nodes[node].get_switches() :
            self._logger.info("Activate switch")
            self._network.nodes[node].set_switch(val,True)

        for val in self._network.nodes[node].get_dimmers() :
            self._logger.info("Activate dimmer : %s" % self._network.nodes[node])
            self._network.nodes[node].set_dimmer(val,99)


    def off(self, address):
        node = int(address)
        for val in self._network.nodes[node].get_switches() :
            self._logger.info("Activate switch")
            self._network.nodes[node].set_switch(val,False)

        for val in self._network.nodes[node].get_dimmers() :
            self._logger.info("Activate dimmer : %s" % self._network.nodes[node])
            self._network.nodes[node].set_dimmer(val,0)

    def status(self, address):
        node = int(address)
        for val in self._network.nodes[node].get_dimmers() :
            level = self._network.nodes[node].get_dimmer_level(val)

