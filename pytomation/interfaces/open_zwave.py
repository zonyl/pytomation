"""
Initial Openzwave support (with Aeon Labs z-stick S2)

by texnofobix@gmail.com

Currently only controls switches and dimmers
"""

#from .common import *
from pytomation.interfaces import State, Command
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
    VERSION = '0.0.4'

    def louie_network_ready(self, network):
        self._logger.info(">>>>>>> Hello from network : I'm ready : %d nodes were found.".format(self._network.nodes_count))
        self._logger.info(">>>>>>> Hello from network : my controller is : {}".format(self._network.controller))
        dispatcher.connect(self.louie_node_update, ZWaveNetwork.SIGNAL_NODE)
        dispatcher.connect(self.louie_value_update, ZWaveNetwork.SIGNAL_VALUE)

    def louie_node_update(self, network, node):
        self._logger.debug('>>>>>>> Hello from node : {}.'.format(node))

    def louie_value_update(self, network, node, value):
        self._logger.debug('>>>>>>> Hello from value : {}'.format(value))
        for lockvalue in self.get_door_locks(node.node_id).values():
            if lockvalue.value_id == value.value_id:
                if value.data:
                    self._onCommand(address=str(node.node_id), command=Command.LOCK)
                else:
                    self._onCommand(address=str(node.node_id), command=Command.UNLOCK)
        for val in self._network.nodes[node.node_id].get_switches():
            if val == value.value_id:
                if value.data:
                    self._onCommand(address=str(node.node_id), command=Command.ON)
                else:
                    self._onCommand(address=str(node.node_id), command=Command.OFF)
        for val in self._network.nodes[node.node_id].get_dimmers() :
            if val == value.value_id:
                #Poll dimmer to ensure ramp up/down completes
                level = value.data
                if self.dimmer_polled_value.has_key(val):
                    self._logger.debug('>>>>>>> Hello from level : {} {}'.format(level, self.dimmer_polled_value[val]))
                    if level == self.dimmer_polled_value[val]:
                        del self.dimmer_polled_value[val]
                        if level < 2:
                            self._onCommand(address=str(node.node_id), command=Command.OFF)
                        elif level > 98:
                            self._onCommand(address=str(node.node_id), command=Command.ON)
                        else:
                            self._onCommand(address=str(node.node_id), command=(Command.LEVEL,level))
                    else:
                        self.dimmer_polled_value[val] = level
                        time.sleep(1)
                        value.refresh()
                else:
                    time.sleep(1)
                    self.dimmer_polled_value[val] = level
                    value.refresh()

    def __init__(self, *args, **kwargs):
        self._serialDevicePath = kwargs.get('serialDevicePath', None)
        self._configpath = kwargs.get('config_path', "/etc/openzwave/")
        super(Open_zwave, self).__init__(self, *args, **kwargs)
        self.dimmer_polled_value = {}

    def _init(self, *args, **kwargs):
        self.awake = False
        self.ready = False
        self.nodesdisplayed = False
        self._options = ZWaveOption(self._serialDevicePath, \
          config_path=self._configpath, \
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
        super(Open_zwave, self)._init(self, *args, **kwargs)

    def _printNetwork(self, node):
        node = self._network.nodes[node]
        self._logger.info("------------------------------------------------------")
        self._logger.info("{} - Name : {}".format(node.node_id,
            node.name))
        self._logger.info("{} - Manufacturer name / id : {} / {}".format(
            node.node_id,
            node.manufacturer_name,
            node.manufacturer_id))
        self._logger.info("{} - Product name / id / type : {} / {} / {}".format(
            node.node_id,
            node.product_name,
            node.product_id,
            node.product_type))
        self._logger.info("{} - Version : {}".format(node.node_id,
            node.version))
        self._logger.info("{} - Command classes : {}".format(node.node_id,
            node.command_classes_as_string))
        self._logger.info("{} - Capabilities : {}".format(node.node_id,
            node.capabilities))
        self._logger.info("{} - Neighbors : {}".format(node.node_id,
            node.neighbors))
        self._logger.info("{} - Can sleep : {}".format(node.node_id,
            node.can_wake_up()))
        for value in self.get_door_locks(node.node_id, 'All').values():
            self._logger.debug("{} - {} : {}".format(node.node_id,value.label,value.data))

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
            self._logger.debug("Not awaked")
        elif self.awake and not self.ready:
            self._logger.debug("Not ready")
        elif not self.nodesdisplayed and self.ready:
            for node in self._network.nodes:
                self._printNetwork(node)
            self.update_status()
            self.nodesdisplayed = True
        time.sleep(1)

    def version(self):
        self._logger.info("Open_zwave Pytomation Driver version " +
                          self.VERSION)
        self._logger.info("Use openzwave library : {}".format(self._network.controller.ozw_library_version))
        self._logger.info("Use python library : {}".format(self._network.controller.python_library_version))
        self._logger.info("Use ZWave library : {}".format(self._network.controller.library_description))
        
    def get_door_locks(self, node, datatype = 'Bool'):
        return self._network.nodes[node].get_values(class_id=0x62, genre='User', \
            type=datatype, readonly=False, writeonly=False)
        
    def lock(self, address):
        node = int(address)
        for value in self.get_door_locks(node).values():
            self._logger.debug("Lock")
            value.data = True
    
    def unlock(self, address):
        node = int(address)
        for value in self.get_door_locks(node).values():
            self._logger.debug("Unlock")
            value.data = False

    def on(self, address):
        node = int(address)
        for val in self._network.nodes[node].get_switches() :
            self._logger.debug("Activate switch")
            self._network.nodes[node].set_switch(val,True)

        for val in self._network.nodes[node].get_dimmers() :
            self._logger.debug("Activate dimmer : {}".format(self._network.nodes[node]))
            self._network.nodes[node].set_dimmer(val,99)

    def off(self, address):
        node = int(address)
        for val in self._network.nodes[node].get_switches() :
            self._logger.debug("Deactivate switch")
            self._network.nodes[node].set_switch(val,False)

        for val in self._network.nodes[node].get_dimmers() :
            self._logger.debug("Deactivate dimmer : {}".format(self._network.nodes[node]))
            self._network.nodes[node].set_dimmer(val,0)

    def level(self, address, level):
        node = int(address)
        for val in self._network.nodes[node].get_dimmers() :
            self._logger.debug("Set dimmer : {}".format(self._network.nodes[node]))
            self._network.nodes[node].set_dimmer(val, level)

    def status(self, address):
        node = int(address)
        for val in self._network.nodes[node].get_switches() :
            level = self._network.nodes[node].get_switch_state(val)
            if level:
                self._onState(address=address, state=State.ON)
            else:
                self._onState(address=address, state=State.OFF)
        for val in self._network.nodes[node].get_dimmers() :
            level = self._network.nodes[node].get_dimmer_level(val)
            if level < 2:
                self._onState(address=address, state=State.OFF)
            elif level > 98:
                self._onState(address=address, state=State.ON)
            else:
                self._onState(address=address, state=(State.LEVEL,level))
        for value in self.get_door_locks(node).values():
            if value.data:
                self._onState(address=address, state=State.LOCKED)
            else:
                self._onState(address=address, state=State.UNLOCKED)

    def update_status(self):
        for d in self._devices:
            self.status(d.address)
