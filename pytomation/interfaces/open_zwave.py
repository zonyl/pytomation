"""
Initial Openzwave support (with Aeon Labs z-stick S2)

by texnofobix@gmail.com

Currently only prints out nodes on network
"""

#from .common import *
from .ha_interface import HAInterface

import time
try:
    #import openzwave
    from openzwave.option import ZWaveOption
    from openzwave.network import ZWaveNetwork
    #from openzwave.node import ZWaveNode
except:
    print ("Error importing Openzwave and/or Python-Openzwave")


class Open_zwave(HAInterface):
    VERSION = '0.0.1'
    awake = False
    ready = False
    nodesdisplayed = False

    def __init__(self, *args, **kwargs):
        self._serialDevicePath = kwargs.get('serialDevicePath', None)
        self._options = ZWaveOption(self._serialDevicePath, \
          config_path="/usr/share/python-openzwave/config", \
          user_path=".", cmd_line="")
        self._options.set_log_file("OZW_Log.log")
        self._options.set_append_log_file(False)
        self._options.set_console_output(True)
        #self._options.set_save_log_level(log)
        self._options.set_save_log_level('Info')
        self._options.set_logging(False)
        self._options.lock()
        self._network = ZWaveNetwork(self._options, log=None)
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
        val = self._network.get_value_from_id_on_network(address)
        nodeid = val.parent_id 
        if (self._network.nodes[nodeid].set_dimmer(val.value_id, 99)):
           self._logger.debug('Command dimmer on at' + address)
	if (self._network.nodes[nodeid].set_switch(val, True)):
           self._logger.debug('Command switch on at' + address)

    def off(self, address):
        val = self._network.get_value_from_id_on_network(address)
        nodeid = val.parent_id 
        if (self._network.nodes[nodeid].set_dimmer(val.value_id, 0)):
           self._logger.debug('Command dimmer off at' + address)
	if (self._network.nodes[nodeid].set_switch(val, False)):
           self._logger.debug('Command switch off at' + address)

    def status(self,address):
        val = self._network.get_value_from_id_on_network(address)
	nodeid = val.parent_id
	level = self._network.nodes[nodeid].get_dimmer_level(val)
	#next lone isn't great
	self._network.nodes[nodeid].set_dimmer(val.value_id, level) 
