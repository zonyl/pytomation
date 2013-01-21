import time

from unittest import TestCase
from datetime import datetime

from pytomation.devices import StateDevice, State, Attribute, Attributes
from pytomation.interfaces import Command

class StateTests(TestCase):
    def test_instance(self):
        self.assertIsNotNone(StateDevice())

    def test_unknown_initial(self):
        self.assertEqual(StateDevice().state, State.UNKNOWN)

    def test_initial(self):
        device = StateDevice(
                        initial=State.ON
                        )
        self.assertEqual(device.state, State.ON)
        self.assertEqual(device.last_command, Command.ON)
    
    def test_initial_from_device(self):
        d1 = StateDevice(
                          )
        self.assertEqual(d1.state, State.UNKNOWN)
        d1.on()
        self.assertEqual(d1.state, State.ON)
        d2 = StateDevice(devices=d1)
        self.assertEqual(d2.state, State.ON)
    
    def test_initial_delegate(self):
        d1 = StateDevice()
        d1.on()
        d2 = StateDevice(devices=(d1),
                          initial=d1)
        self.assertEqual(d2.state, State.ON)
        
    def test_command_on(self):
        device = StateDevice()
        self.assertEqual(device.state, State.UNKNOWN)
        device.on()
        self.assertEqual(device.state, State.ON)

    def test_command_subcommand(self):
        device = StateDevice()
        self.assertEqual(device.state, State.UNKNOWN)
        device.level(80)
        self.assertEqual(device.state, (State.LEVEL, 80))
        
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
        device = StateDevice(
#                              time=Attributes(command=Command.OFF,
#                                              time=(trigger_time1, trigger_time2)
#                                              )
#                              )
                              time={
                                    
                                    'command': Command.OFF,
                                    'time': (trigger_time1, trigger_time2),
                                    }
                              )
        self.assertEqual(device.state, State.UNKNOWN)
        time.sleep(3)
        print datetime.now()
        self.assertEqual(device.state, State.OFF)
        device.on()
        time.sleep(3)
        print datetime.now()
        print device._times
        self.assertEqual(device.state, State.OFF)
        
    def test_binding(self):
        d1 = StateDevice()
        d1.off()
        self.assertEqual(d1.state, State.OFF)
        d2 = StateDevice(devices=d1)
        self.assertEqual(d2.state, State.OFF)
        d1.on()
        self.assertEqual(d2.state, State.ON)
        
    def test_binding_default(self):
        d1 = StateDevice()
        d1.off()
        d2 = StateDevice(d1)
        self.assertEqual(d2.state, State.OFF)
        d1.on()
        self.assertEqual(d2.state, State.ON)

        
    def test_map(self):
        d1 = StateDevice()
        d2 = StateDevice()
        d3 = StateDevice(devices=(d1, d2),
                          mapped={'command': Command.ON,
                                   'mapped': Command.OFF,
                                   'source': d2}
                          )
        self.assertEqual(d3.state, State.UNKNOWN)
        d1.on()
        self.assertEqual(d3.state, State.ON)
        d2.on()
        self.assertEqual(d3.state, State.OFF)
        
    def test_delay(self):
        d1 = StateDevice()
        d2 = StateDevice(devices=d1,
                          delay={'command': Command.OFF,
                                 'mapped': (Command.LEVEL, 80),
                                 'source': d1,
                                 'secs': 2,
                                 })
        self.assertEqual(d2.state, State.UNKNOWN)
        d1.on()
        self.assertEqual(d2.state, State.ON)
        d1.off()
        self.assertEqual(d2.state, State.ON)
        time.sleep(3)
#        time.sleep(2000)
        self.assertEqual(d2.state, (State.LEVEL, 80))
        
    def test_delay_zero_secs(self):
        d1 = StateDevice()
        d2 = StateDevice()
        d3 = StateDevice(
                         devices=(d1, d2),
                         delay=({
                                Attribute.COMMAND: Command.OFF,
                                Attribute.SECS: 2
                                },
                                {
                                 Attribute.COMMAND: Command.OFF,
                                 Attribute.SECS: 0,
                                 Attribute.SOURCE: d2,
                                 }
                                ),
                         initial=State.ON,
                         )    
        self.assertEqual(d3.state, State.ON)
        d1.off()
        self.assertEqual(d3.state, State.ON)
        time.sleep(3)
        self.assertEqual(d3.state, State.OFF)
        d3.on()
        self.assertEqual(d3.state, State.ON)
        d2.off()
        self.assertEqual(d3.state, State.OFF)
        
        
    def test_delay_no_retrigger(self):
        d1 = StateDevice(trigger={
                                 Attribute.COMMAND: Command.ON,
                                 Attribute.MAPPED: Command.OFF,
                                 Attribute.SECS: 3},
                          delay={
                                 Attribute.COMMAND: Command.OFF,
                                 Attribute.SECS: 3},
                          )
        d1.on()
        self.assertEqual(d1.state, State.ON)
        d1.off()
        self.assertEqual(d1.state, State.ON)
        time.sleep(2)
        d1.off()
        time.sleep(1)
        self.assertEqual(d1.state, State.OFF)
        
                
    def test_delay_single(self):
        d1 = StateDevice(
                          delay={'command': Command.OFF,
                                 'secs': 2,
                                 }
                          )
        self.assertEqual(d1.state, State.UNKNOWN)
        d1.on()
        self.assertEqual(d1.state, State.ON)
        d1.off()
        self.assertEqual(d1.state, State.ON)
        time.sleep(3)
#        time.sleep(20000)
        self.assertEqual(d1.state, State.OFF)

    def test_delay_multiple(self):
        d1 = StateDevice()
        d2 = StateDevice()
        d3 = StateDevice(
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
        self.assertEqual(d3.state, State.UNKNOWN)
        d3.on()
        self.assertEqual(d3.state, State.ON)
        d1.off()
        self.assertEqual(d3.state, State.ON)
        time.sleep(3)
        self.assertEqual(d3.state, State.OFF)
        
        #d2
        d3.on()
        self.assertEqual(d3.state, State.ON)
        d2.off()
        self.assertEqual(d3.state, State.ON)
        time.sleep(3)
        self.assertEqual(d3.state, State.ON)
        time.sleep(1)
        self.assertEqual(d3.state, State.OFF)
        
    def test_delay_priority(self):
        d1 = StateDevice()
        d2 = StateDevice()
        d3 = StateDevice(
                         devices=(d1,d2),
                         delay=({
                                Attribute.COMMAND: Command.OFF,
                                Attribute.SOURCE: d1,
                                Attribute.SECS: 4,
                                },
                                {
                                 Attribute.COMMAND: Command.OFF,
                                 Attribute.SECS: 2
                                 },
                                ),
                         initial=State.ON,
                         )
        self.assertEqual(d3.state, State.ON)
        d1.off()
        self.assertEqual(d3.state, State.ON)
        time.sleep(2)
        self.assertEqual(d3.state, State.ON)
        time.sleep(2)
        self.assertEqual(d3.state, State.OFF)
        
        
    def test_idle_time_property(self):
        d = StateDevice()
        d.on()
        time.sleep(2)
        self.assertTrue(d.idle_time >= 2)
        
    def test_idle_timer(self):
        s1 = StateDevice()
        s2 = StateDevice(devices=s1,
                         idle={
                               'command': State.OFF,
                               'secs': 2,
                               }
                         )
        s1.on()
        self.assertEqual(s2.state, State.ON)
        time.sleep(3)
        self.assertEqual(s2.state, State.OFF)
        s1.on()
        self.assertEqual(s2.state, State.ON)

    def test_ignore_state(self):
        s1 = StateDevice()
        s2 = StateDevice(devices = s1,
                          ignore={
                                  'command': Command.ON,
                                  'source:': s1,
                                  },
                          )
        s1.on()
        self.assertEqual(s2.state, State.UNKNOWN)
        s1.off()
        self.assertEqual(s2.state, State.OFF)
        s1.on()
        self.assertEqual(s2.state, State.OFF)

    def test_ignore_multiple_state(self):
        s1 = StateDevice()
        s2 = StateDevice(devices = s1,
                          ignore=({
                                  Attribute.COMMAND: Command.ON,
                                  },
                                  {
                                   Attribute.COMMAND: Command.OFF,
                                   }
                                  ),
                          )
        self.assertEqual(s2.state, State.UNKNOWN)
        s1.on()
        self.assertEqual(s2.state, State.UNKNOWN)
        s1.off()
        self.assertEqual(s2.state, State.UNKNOWN)
        s1.on()
        self.assertEqual(s2.state, State.UNKNOWN)

    def test_ignore_multiples_state(self):
        s1 = StateDevice()
        s2 = StateDevice(devices = s1,
                          ignore={
                                  Attribute.COMMAND: (Command.ON, Command.OFF)
                                  },
                          )
        self.assertEqual(s2.state, State.UNKNOWN)
        s1.on()
        self.assertEqual(s2.state, State.UNKNOWN)
        s1.off()
        self.assertEqual(s2.state, State.UNKNOWN)
        s1.on()
        self.assertEqual(s2.state, State.UNKNOWN)


    def test_last_command(self):
        s1 = StateDevice()
        s1.on()
        self.assertEqual(s1.state, State.ON)
        s1.off()
        self.assertEqual(s1.state, State.OFF)
        self.assertEqual(s1.last_command, Command.OFF)

    def test_previous_state_command(self):
        s1 = StateDevice()
        s1.on()
        self.assertEqual(s1.state, State.ON)
        s1.off()
        self.assertEqual(s1.state, State.OFF)
        s1.previous()
        self.assertEqual(s1.state, State.ON)

    def test_toggle_state(self):
        s1 = StateDevice()
        s1.on()
        self.assertEqual(s1.state, State.ON)
        s1.toggle()
        self.assertEqual(s1.state, State.OFF)
        s1.toggle()
        self.assertEqual(s1.state, State.ON)
        
    def test_trigger(self):
        s1 = StateDevice(
                          trigger={
                                   'command': Command.ON,
                                   'mapped': Command.OFF,
                                   'secs': 2
                                   }
                          )
        s1.on();
        self.assertEqual(s1.state, State.ON)
        time.sleep(3)
        self.assertEqual(s1.state, State.OFF)
        
    def test_initial_attribute(self):
        d = StateDevice(
                         name='pie'
                         )
        self.assertEqual(d.name, 'pie')
        
    def test_delay_multiple_source(self):
        d1 = StateDevice()
        d2 = StateDevice()
        d3 = StateDevice()
        d4 = StateDevice(
                          devices=(d1, d2, d3),
                          delay={
                                 Attribute.COMMAND: Command.OFF,
                                 Attribute.SOURCE: (d1, d2),
                                 Attribute.SECS: 2,
                                },
                          )
        d1.on()
        self.assertEqual(d4.state, State.ON)
        d1.off()
        self.assertEqual(d4.state, State.ON)
        time.sleep(3)
        self.assertEqual(d4.state, State.OFF)

        d3.on()
        self.assertEqual(d4.state, State.ON)
        d3.off()
        self.assertEqual(d4.state, State.OFF)
        
    def test_override_default_maps(self):
        d = StateDevice(
                         mapped={
                                 Attribute.COMMAND: Command.ON,
                                 Attribute.MAPPED: Command.OFF,
                                 }
                         )
        d.on()
        self.assertEqual(d.state, State.OFF)
        
        
    def test_map_delay(self):
        d = StateDevice(
                         mapped={
                                 Attribute.COMMAND: Command.ON,
                                 Attribute.MAPPED: Command.OFF,
                                 Attribute.SECS: 2,
                                 },
                         )
        self.assertEqual(d.state, State.UNKNOWN)
        d.on()
        self.assertEqual(d.state, State.UNKNOWN)
        time.sleep(3)
        self.assertEqual(d.state, Command.OFF)
        
    def test_map_sources(self):
        d1 = StateDevice()
        d2 = StateDevice()
        d3 = StateDevice()
        d4 = StateDevice(
                          devices=(d1, d2, d3),
                          mapped={
                                  Attribute.COMMAND: Command.ON,
                                  Attribute.SOURCE: (d1, d2),
                                  Attribute.MAPPED: Command.OFF,
                                  }
                          )
        self.assertEqual(d4.state, State.UNKNOWN)
        d3.on()
        self.assertEqual(d4.state, State.ON)
        d2.on()
        self.assertEqual(d4.state, State.OFF)
        
        

        