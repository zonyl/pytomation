"""
Initial Openzwave support (with Aeon Labs z-stick S2)

by texnofobix@gmail.com

Currently only prints out nodes on network
"""

from .common import *
from .ha_interface import HAInterface

import openzwave
from openzwave.option import ZWaveOption
from openzwave.network import ZWaveNetwork
#from openzwave.node import ZWaveNode
# except: 
#     self._logger.error("Openzwave and/or Python-Openzwave")
    
class Open_zwave(HAInterface):
    VERSION='0.0.1'
    awake=False
    ready=False
    nodesdisplayed=False
    
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
        

    def _init(self, *args, **kwargs):   
        super(Open_zwave, self)._init(self, *args, **kwargs)

    def _readInterface(self, lastPacketHash):
        if self._network.state>=self._network.STATE_AWAKED and not self.awake:
            self.awake = True
            self._logger.info("Network Awaked")
        if self._network.state>=self._network.STATE_READY and not self.ready:
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
        if not nodesdisplayed:           
            for node in self._network.nodes:
                print
                print "------------------------------------------------------------"
                print "%s - Name : %s" % (self._network.nodes[node].node_id,self._network.nodes[node].name)
                print "%s - Manufacturer name / id : %s / %s" % (self._network.nodes[node].node_id,self._network.nodes[node].manufacturer_name, self._network.nodes[node].manufacturer_id)
                print "%s - Product name / id / type : %s / %s / %s" % (self._network.nodes[node].node_id,self._network.nodes[node].product_name, self._network.nodes[node].product_id, self._network.nodes[node].product_type)
                print "%s - Version : %s" % (self._network.nodes[node].node_id, self._network.nodes[node].version)
                print "%s - Command classes : %s" % (self._network.nodes[node].node_id,self._network.nodes[node].command_classes_as_string)
                print "%s - Capabilities : %s" % (self._network.nodes[node].node_id,self._network.nodes[node].capabilities)
                print "%s - Neigbors : %s" % (self._network.nodes[node].node_id,self._network.nodes[node].neighbors)
                print "%s - Can sleep : %s" % (self._network.nodes[node].node_id,self._network.nodes[node].can_wake_up())
            nodesdisplayed=True
    
    def version(self):
        self._logger.info("Open_zwave Pytomation Driver version " + self.VERSION)
        self._logger.info("Use openzwave library : %s" % self._network.controller.ozw_library_version)
        self._logger.info("Use python library : %s" % self._network.controller.python_library_version)
        self._logger.info("Use ZWave library : %s" % self._network.controller.library_description)
        