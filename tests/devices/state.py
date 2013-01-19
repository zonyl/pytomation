import time

from unittest import TestCase
from datetime import datetime

from pytomation.devices import State2Device, State2, Attribute, Attributes
from pytomation.interfaces import Command

class State2Tests(TestCase):
    def test_instance(self):
        self.assertIsNotNone(State2Device())

    def test_unknown_initial(self):
        self.assertEqual(State2Device().state, State2.UNKNOWN)

    def test_initial(self):
        device = State2Device(
                        initial=State2.ON
                        )
        self.assertEqual(device.state, State2.ON)
        self.assertEqual(device.last_command, Command.ON)
    
    def test_initial_from_device(self):
        d1 = State2Device(
                          )
        self.assertEqual(d1.state, State2.UNKNOWN)
        d1.on()
        self.assertEqual(d1.state, State2.ON)
        d2 = State2Device(devices=d1)
        self.assertEqual(d2.state, State2.ON)
    
    def test_initial_delegate(self):
        d1 = State2Device()
        d1.on()
        d2 = State2Device(devices=(d1),
                          initial=d1)
        self.assertEqual(d2.state, State2.ON)
        
    def test_command_on(self):
        device = State2Device()
        self.assertEqual(device.state, State2.UNKNOWN)
        device.on()
        self.assertEqual(device.state, State2.ON)

    def test_command_subcommand(self):
        device = State2Device()
        self.assertEqual(device.state, State2.UNKNOWN)
        device.level(80)
        self.assertEqual(device.state, (State2.LEVEL, 80))
        
    def test_time_off(self):
        now = datetime.now()
        hours, mins, secs = now.timetuple()[3:6]
        secs = (secs + 2) % 60
        mins += (secs + 2) / 60
        trigger_time1 = '{h}:{m}:{s}'.format(
                                             h=hours,
                                             m=mins,
                                             s=secs,
                                                 )
        print 'Trigger Time' + trigger_time1
        secs = (secs + 2) % 60
        mins += (secs + 2) / 60
        trigger_time2 = '{h}:{m}:{s}'.format(
                                             h=hours,
                                             m=mins,
                                             s=secs,
                                                 )
        print 'Trigger Time' + trigger_time2
        device = State2Device(
#                              time=Attributes(command=Command.OFF,
#                                              time=(trigger_time1, trigger_time2)
#                                              )
#                              )
                              time={
                                    
                                    'command': Command.OFF,
                                    'time': (trigger_time1, trigger_time2),
                                    }
                              )
        self.assertEqual(device.state, State2.UNKNOWN)
        time.sleep(3)
        print datetime.now()
        self.assertEqual(device.state, State2.OFF)
        device.on()
        time.sleep(3)
        print datetime.now()
        print device._times
        self.assertEqual(device.state, State2.OFF)
        
    def test_binding(self):
        d1 = State2Device()
        d1.off()
        self.assertEqual(d1.state, State2.OFF)
        d2 = State2Device(devices=d1)
        self.assertEqual(d2.state, State2.OFF)
        d1.on()
        self.assertEqual(d2.state, State2.ON)
        
    def test_binding_default(self):
        d1 = State2Device()
        d1.off()
        d2 = State2Device(d1)
        self.assertEqual(d2.state, State2.OFF)
        d1.on()
        self.assertEqual(d2.state, State2.ON)

        
    def test_map(self):
        d1 = State2Device()
        d2 = State2Device()
        d3 = State2Device(devices=(d1, d2),
                          mapped={'command': Command.ON,
                                   'mapped': Command.OFF,
                                   'source': d2}
                          )
        self.assertEqual(d3.state, State2.UNKNOWN)
        d1.on()
        self.assertEqual(d3.state, State2.ON)
        d2.on()
        self.assertEqual(d3.state, State2.OFF)
        
    def test_delay(self):
        d2 = State2Device()
        d1 = State2Device(devices=d2,
                          delay={'command': Command.OFF,
                                 'mapped': (Command.LEVEL, 80),
                                 'source': d2,
                                 'secs': 2,
                                 })
        self.assertEqual(d1.state, State2.UNKNOWN)
        d2.on()
        self.assertEqual(d1.state, State2.ON)
        d2.off()
        self.assertEqual(d1.state, State2.ON)
        time.sleep(3)
#        time.sleep(2000)
        self.assertEqual(d1.state, (State2.LEVEL, 80))
        
    def test_delay_no_retrigger(self):
        d1 = State2Device(trigger={
                                 Attribute.COMMAND: Command.ON,
                                 Attribute.MAPPED: Command.OFF,
                                 Attribute.SECS: 3},
                          delay={
                                 Attribute.COMMAND: Command.OFF,
                                 Attribute.SECS: 3},
                          )
        d1.on()
        self.assertEqual(d1.state, State2.ON)
        d1.off()
        self.assertEqual(d1.state, State2.ON)
        time.sleep(2)
        d1.off()
        time.sleep(1)
        self.assertEqual(d1.state, State2.OFF)
        
                
    def test_delay_single(self):
        d1 = State2Device(
                          delay={'command': Command.OFF,
                                 'secs': 2,
                                 }
                          )
        self.assertEqual(d1.state, State2.UNKNOWN)
        d1.on()
        self.assertEqual(d1.state, State2.ON)
        d1.off()
        self.assertEqual(d1.state, State2.ON)
        time.sleep(3)
#        time.sleep(20000)
        self.assertEqual(d1.state, State2.OFF)

    def test_delay_multiple(self):
        d1 = State2Device()
        d2 = State2Device()
        d3 = State2Device(
                          devices=(d1, d2),
                          delay=(
                                     {Attribute.COMMAND: (Command.OFF),
                                     Attribute.SOURCE: (d1),
                                     Attribute.SECS: 2,
                                     },
                                     {Attribute.COMMAND: Command.OFF,
                                     Attribute.SOURCE: d2,
                                     Attribute.SECS: 4,
                                     },
                                 )
                          )
        self.assertEqual(d3.state, State2.UNKNOWN)
        d3.on()
        self.assertEqual(d3.state, State2.ON)
        d1.off()
        self.assertEqual(d3.state, State2.ON)
        time.sleep(3)
        self.assertEqual(d3.state, State2.OFF)
        
        #d2
        d3.on()
        self.assertEqual(d3.state, State2.ON)
        d2.off()
        self.assertEqual(d3.state, State2.ON)
        time.sleep(3)
        self.assertEqual(d3.state, State2.ON)
        time.sleep(1)
        self.assertEqual(d3.state, State2.OFF)
        

    def test_idle_time_property(self):
        d = State2Device()
        d.on()
        time.sleep(2)
        self.assertTrue(d.idle_time >= 2)
        
    def test_idle_timer(self):
        s1 = State2Device()
        s2 = State2Device(devices=s1,
                         idle={
                               'command': State2.OFF,
                               'secs': 2,
                               }
                         )
        s1.on()
        self.assertEqual(s2.state, State2.ON)
        time.sleep(3)
        self.assertEqual(s2.state, State2.OFF)
        s1.on()
        self.assertEqual(s2.state, State2.ON)

    def test_ignore_state(self):
        s1 = State2Device()
        s2 = State2Device(devices = s1,
                          ignore={
                                  'command': Command.ON,
                                  'source:': s1,
                                  },
                          )
        s1.on()
        self.assertEqual(s2.state, State2.UNKNOWN)
        s1.off()
        self.assertEqual(s2.state, State2.OFF)
        s1.on()
        self.assertEqual(s2.state, State2.OFF)

    def test_ignore_multiple_state(self):
        s1 = State2Device()
        s2 = State2Device(devices = s1,
                          ignore=({
                                  Attribute.COMMAND: Command.ON,
                                  },
                                  {
                                   Attribute.COMMAND: Command.OFF,
                                   }
                                  ),
                          )
        self.assertEqual(s2.state, State2.UNKNOWN)
        s1.on()
        self.assertEqual(s2.state, State2.UNKNOWN)
        s1.off()
        self.assertEqual(s2.state, State2.UNKNOWN)
        s1.on()
        self.assertEqual(s2.state, State2.UNKNOWN)

    def test_ignore_multiples_state(self):
        s1 = State2Device()
        s2 = State2Device(devices = s1,
                          ignore={
                                  Attribute.COMMAND: (Command.ON, Command.OFF)
                                  },
                          )
        self.assertEqual(s2.state, State2.UNKNOWN)
        s1.on()
        self.assertEqual(s2.state, State2.UNKNOWN)
        s1.off()
        self.assertEqual(s2.state, State2.UNKNOWN)
        s1.on()
        self.assertEqual(s2.state, State2.UNKNOWN)


    def test_last_command(self):
        s1 = State2Device()
        s1.on()
        self.assertEqual(s1.state, State2.ON)
        s1.off()
        self.assertEqual(s1.state, State2.OFF)
        self.assertEqual(s1.last_command, Command.OFF)

    def test_previous_state_command(self):
        s1 = State2Device()
        s1.on()
        self.assertEqual(s1.state, State2.ON)
        s1.off()
        self.assertEqual(s1.state, State2.OFF)
        s1.previous()
        self.assertEqual(s1.state, State2.ON)

    def test_toggle_state(self):
        s1 = State2Device()
        s1.on()
        self.assertEqual(s1.state, State2.ON)
        s1.toggle()
        self.assertEqual(s1.state, State2.OFF)
        s1.toggle()
        self.assertEqual(s1.state, State2.ON)
        
    def test_trigger(self):
        s1 = State2Device(
                          trigger={
                                   'command': Command.ON,
                                   'mapped': Command.OFF,
                                   'secs': 2
                                   }
                          )
        s1.on();
        self.assertEqual(s1.state, State2.ON)
        time.sleep(3)
        self.assertEqual(s1.state, State2.OFF)
        
    def test_initial_attribute(self):
        d = State2Device(
                         name='pie'
                         )
        self.assertEqual(d.name, 'pie')
        
    def test_delay_multiple_source(self):
        d1 = State2Device()
        d2 = State2Device()
        d3 = State2Device()
        d4 = State2Device(
                          devices=(d1, d2, d3),
                          delay={
                                 Attribute.COMMAND: Command.OFF,
                                 Attribute.SOURCE: (d1, d2),
                                 Attribute.SECS: 2,
                                },
                          )
        d1.on()
        self.assertEqual(d4.state, State2.ON)
        d1.off()
        self.assertEqual(d4.state, State2.ON)
        time.sleep(3)
        self.assertEqual(d4.state, State2.OFF)

        d3.on()
        self.assertEqual(d4.state, State2.ON)
        d3.off()
        self.assertEqual(d4.state, State2.OFF)
        
    def test_override_default_maps(self):
        d = State2Device(
                         mapped={
                                 Attribute.COMMAND: Command.ON,
                                 Attribute.MAPPED: Command.OFF,
                                 }
                         )
        d.on()
        self.assertEqual(d.state, State2.OFF)
        
        
    def test_map_delay(self):
        d = State2Device(
                         mapped={
                                 Attribute.COMMAND: Command.ON,
                                 Attribute.MAPPED: Command.OFF,
                                 Attribute.SECS: 2,
                                 },
                         )
        self.assertEqual(d.state, State2.UNKNOWN)
        d.on()
        self.assertEqual(d.state, State2.UNKNOWN)
        time.sleep(3)
        self.assertEqual(d.state, Command.OFF)
        
    def test_map_sources(self):
        d1 = State2Device()
        d2 = State2Device()
        d3 = State2Device()
        d4 = State2Device(
                          devices=(d1, d2, d3),
                          mapped={
                                  Attribute.COMMAND: Command.ON,
                                  Attribute.SOURCE: (d1, d2),
                                  Attribute.MAPPED: Command.OFF,
                                  }
                          )
        self.assertEqual(d4.state, State2.UNKNOWN)
        d3.on()
        self.assertEqual(d4.state, State2.ON)
        d2.on()
        self.assertEqual(d4.state, State2.OFF)
        
        

        