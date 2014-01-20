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
        
    def test_time_cron_off(self):
        now = datetime.now()
        hours, mins, secs = now.timetuple()[3:6]
        secs = (secs + 2) % 60
        mins += (secs + 2) / 60
        ctime = (secs, mins, hours)
        
        s = StateDevice(
                       time={
                             Attribute.COMMAND: Command.OFF,
                             Attribute.TIME: ctime,
                             }
                       )
        s.on()
        self.assertEqual(s.state, Command.ON)
        time.sleep(3)
        self.assertEqual(s.state, Command.OFF)

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
                               Attribute.MAPPED: State.OFF,
                               Attribute.SECS: 2,
                               }
                         )
        s1.on()
        self.assertEqual(s2.state, State.ON)
        time.sleep(3)
        self.assertEqual(s2.state, State.OFF)
        s1.on()
        self.assertEqual(s2.state, State.ON)

    def test_idle_timer_then_trigger(self):
        s1 = StateDevice()
        s2 = StateDevice(devices=s1,
                         trigger={
                                Attribute.COMMAND: State.ON,
                                Attribute.MAPPED: State.OFF,
                                Attribute.SECS: 4,
                                },
                         idle={
                               Attribute.MAPPED: State.UNKNOWN,
                               Attribute.SECS: 2,
                               }
                         )
        s1.on()
        self.assertEqual(s2.state, State.ON)
        time.sleep(3)
        self.assertEqual(s2.state, State.UNKNOWN)
        time.sleep(5)
        self.assertEqual(s2.state, State.OFF)
#         s1.on()
#         self.assertEqual(s2.state, State.ON)


        
    def test_idle_source(self):
        s1 = StateDevice()
        s2 = StateDevice()
        s1.off()
        s2.off()
        s3 = StateDevice(devices=(s1, s2),
                          idle={
                                Attribute.MAPPED: State.OFF,
                                Attribute.SECS: 2,
                                Attribute.SOURCE: s2
                                }
                          )
        s1.on()
        self.assertEqual(s3.state, State.ON)
        time.sleep(3)
        self.assertEqual(s3.state, State.ON)
        s2.on()
        self.assertEqual(s3.state, State.ON)
        time.sleep(3)
        self.assertEqual(s3.state, State.OFF)
        

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

    def test_ignore_device(self):
        s1 = StateDevice()
        s2 = StateDevice(devices=s1,
                         ignore={
                                 Attribute.SOURCE: s1
                                 }
                         )
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

    def test_previous_state_twice_command(self):
        s1 = StateDevice()
        s2 = StateDevice(devices=s1)
        s1.off()
        self.assertEqual(s1.state, State.OFF)
        s1.on()
        self.assertEqual(s1.state, State.ON)
        s1.on()
        self.assertEqual(s1.state, State.ON)
        s1.previous()
        self.assertEqual(s1.state, State.OFF)
        
        
        
        
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

    def test_trigger_time_range(self):
        (s_h, s_m, s_s) = datetime.now().timetuple()[3:6]
        e_h = s_h
        e_m = s_m
        e_s = s_s + 2
        s = StateDevice()
        s2 = StateDevice(devices=s,
                         trigger={
                                Attribute.COMMAND: Command.ON,
                                Attribute.MAPPED: Command.OFF,
                                Attribute.SECS: 1,
                                 Attribute.START: '{h}:{m}:{s}'.format(
                                                                      h=s_h,
                                                                      m=s_m,
                                                                      s=s_s,
                                                                      ),
                                 Attribute.END: '{h}:{m}:{s}'.format(
                                                                      h=e_h,
                                                                      m=e_m,
                                                                      s=e_s,
                                                                      ),
                                 },
                         
                         )
        self.assertEqual(s2.state, State.UNKNOWN)
        s.on()
        self.assertEqual(s2.state, State.ON)
        time.sleep(3)
        self.assertEqual(s2.state, State.OFF)
        ##
        time.sleep(2)
        s.on()
        time.sleep(3)
        self.assertEqual(s2.state, State.ON)
      
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
        
    def test_delay_cancel_on_other_state(self):
        d1 = StateDevice()
        d2 = StateDevice(devices=d1,
                         initial=State.OFF,
                         delay={
                                Attribute.COMMAND: Command.OFF,
                                Attribute.SECS: 2,
                                },
                         )
        self.assertEqual(d2.state, State.UNKNOWN)
        d1.on()
        self.assertEqual(d2.state, State.ON)
        d1.off()
        self.assertEqual(d2.state, State.ON)
        d1.on()
        self.assertEqual(d2.state, State.ON)
        time.sleep(3)
        self.assertEqual(d2.state, State.ON)
        
        
    def test_manual_state(self):
        d1 = StateDevice()
        d2 = StateDevice(devices=d1,
                         delay={
                                Attribute.COMMAND: Command.OFF,
                                Attribute.SECS: 2
                                },
                         )
        d2.on()
        self.assertEqual(d2.state, State.ON)
        d2.manual()
        d2.off()
        self.assertEqual(d2.state, State.OFF)
        d2.on()
        d2.automatic()
        d2.off()
        self.assertEqual(d2.state, State.ON)
        time.sleep(3)
        self.assertEqual(d2.state, State.OFF)
                
    def test_changes_only(self):
        d1 = StateDevice()
        d2 = StateDevice(devices=d1,
                         changes_only=True,
                         name='tested')
        d3 = StateDevice(devices=d2)
        d1.off()
        self.assertEqual(d1.state, State.OFF)
        self.assertEqual(d2.state, State.OFF)
        self.assertEqual(d3.state, State.OFF)
        d1.on()
        self.assertEqual(d1.state, State.ON)
        self.assertEqual(d2.state, State.ON)
        self.assertEqual(d3.state, State.ON)
        d3.off()
        self.assertEqual(d3.state, State.OFF)
        # set on again, this time no delegation
        d1.on()
        self.assertEqual(d3.state, State.OFF)

        # after x amount of time still prevent dupes
        time.sleep(3)
        d1.on()
        self.assertEqual(d3.state, State.OFF)
        
    def test_retrigger_delay(self):
        d1 = StateDevice()
        d2 = StateDevice(devices=d1,
                         retrigger_delay={
                                   Attribute.SECS: 2
                                   },
                         name='tested')
        d3 = StateDevice(devices=d2)
        d1.off()
        self.assertEqual(d1.state, State.OFF)
        self.assertEqual(d2.state, State.OFF)
        self.assertEqual(d3.state, State.OFF)
        d1.on()
        self.assertEqual(d1.state, State.ON)
        self.assertEqual(d2.state, State.ON)
        self.assertEqual(d3.state, State.ON)
        d3.off()
        self.assertEqual(d3.state, State.OFF)
        # set on again, this time no delegation
        d1.on()
        self.assertEqual(d3.state, State.OFF)
        
        # after x amount of time allow dupes
        time.sleep(3)
        d1.on()
        self.assertEqual(d3.state, State.ON)
        
    def test_loop_prevention(self):
        s1 = StateDevice()
        s2 = StateDevice()
        s1.devices(s2)
        s2.devices(s1)
        s1.on()
        pass
    
    def test_state_remove_device(self):
        s1 = StateDevice()
        s2 = StateDevice(devices=s1)
        s1.on()
        self.assertEqual(s2.state, State.ON)
        s2.off()
        self.assertEqual(s2.state, State.OFF)        
        r=s2.remove_device(s1)
        self.assertTrue(r)
        self.assertEqual(s2.state, State.OFF)        
        s1.on()
        self.assertEqual(s2.state, State.OFF)     
        # remove again and not error
        r = s2.remove_device(s1)
        self.assertFalse(r)
        
    def test_state_ignore_range(self):
        (s_h, s_m, s_s) = datetime.now().timetuple()[3:6]
        e_h = s_h
        e_m = s_m
        e_s = s_s + 2
        s = StateDevice()
        s2 = StateDevice(devices=s,
                         ignore={
                                 Attribute.SOURCE: s,
                                 Attribute.START: '{h}:{m}:{s}'.format(
                                                                      h=s_h,
                                                                      m=s_m,
                                                                      s=s_s,
                                                                      ),
                                 Attribute.END: '{h}:{m}:{s}'.format(
                                                                      h=e_h,
                                                                      m=e_m,
                                                                      s=e_s,
                                                                      ),
                                 },
                         
                         )
        self.assertEqual(s2.state, State.UNKNOWN)
        s.on()
        self.assertEqual(s2.state, State.UNKNOWN)
        time.sleep(3)
        s.on()
        self.assertEqual(s2.state, State.ON)
        
    def test_ignore_multi_command(self):
        s1 = StateDevice()
        s2 = StateDevice(devices=s1,
                         ignore={
                                 Attribute.COMMAND: (Command.ON, Command.OFF,)
                                 },
                         )
        self.assertEqual(s2.state, State.UNKNOWN)
        s1.on()
        self.assertEqual(s2.state, State.UNKNOWN)
        s1.off()
        self.assertEqual(s2.state, State.UNKNOWN)
        
        
    def test_status_command(self):
        s = StateDevice()
        s.status()
        self.assertTrue(True)
        
    def test_invalid_constructor_keyword(self):
        s1 = StateDevice()
        s2 = StateDevice(device=s1) #invalid keyword device
        #If I had implemented a DI framework I could automatically test for an error debug statement.
        # alas I do not.  Need to manually verify this one
        self.assertTrue(True)
        
#     def test_invert_commands(self):
#         s = StateDevice(invert=True)
#         s.on()
#         self.assertEqual(s.state, State.OFF)
#         s.off()
#         self.assertEqual(s.state, State.ON)
#         s.invert(False)
#         s.on()
#         self.assertEqual(s.state, State.ON)

    def test_time_range_invalid(self):
        try:
            s1 = StateDevice(
                             ignore={
                                     Attribute.COMMAND: Command.ON,
                                     Attribute.START: '10:56 am',
                                     Attribute.END: '11.02 am',
                                     }
                             )
            self.assertTrue(False)
        except AssertionError, ex:
            raise ex
        except Exception, ex:
            pass
        

    def test_restriction(self):
        sr = StateDevice()
        s1 = StateDevice()
        s2 = StateDevice(
                         devices=(s1),
                         restriction={
                                      Attribute.SOURCE: sr,
                                      Attribute.STATE: State.ON,
                                      }
                                      
                         )
        self.assertEqual(State.UNKNOWN, s2.state)
        s1.on()
        self.assertEqual(State.ON, s2.state)
        s1.off()
        self.assertEqual(State.OFF, s2.state)
        # Restrict
        sr.on()
        s1.on()
        self.assertEqual(State.OFF, s2.state)
        s1.off()
        sr.off()
        s1.on()
        self.assertEqual(State.ON, s2.state)
        
    def test_restriction_specific_state(self):
        # Dark = ON
        # light = OFF
        sr = StateDevice()
        s2 = StateDevice(
                         devices=(sr),
                         restriction={
                                      Attribute.SOURCE: sr,
                                      Attribute.STATE: State.OFF,
                                      Attribute.TARGET: Command.ON,
                                      }
                         )
                                      
        # Restrict
        sr.on()
        self.assertEqual(State.ON, s2.state)
        sr.off()
        self.assertEqual(State.OFF, s2.state)        
        
        
