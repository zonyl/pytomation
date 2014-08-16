from datetime import datetime
import gc
import thread

from pytomation.common import PytomationObject
from pytomation.interfaces import Command
from pytomation.utility import CronTimer
from pytomation.utility.timer import Timer as CTimer
from pytomation.utility.time_funcs import *

class State(object):
    ALL = 'all'
    UNKNOWN = 'unknown'
    ON = 'on'
    OFF = 'off'
    LEVEL = 'level'
    SETPOINT = 'setpoint'
    MOTION = 'motion'
    STILL = 'still'
    OPEN = 'open'
    CLOSED = "close"
    LIGHT = "light"
    DARK = "dark"
    ACTIVE = 'activate'
    INACTIVE = 'deactivate'
    OCCUPIED = 'occupy'
    VACANT = 'vacate'
    HEAT = 'heat'
    COOL = 'cool'
    CIRCULATE = 'circulate'
    AUTOMATIC = 'automatic'
    HOLD = 'hold'
    

class Attribute(object):
    MAPPED = 'mapped'
    COMMAND = 'command'
    STATE = 'state'
    TARGET = 'target'
    TIME = 'time'
    SECS = 'secs'
    SOURCE = 'source'
    START = 'start'
    END = 'end'

class Property(object):
    IDLE = 'idle'
    DELAY = 'delay'
    
class StateDevice(PytomationObject):
    STATES = [State.UNKNOWN, State.ON, State.OFF, State.LEVEL]
    COMMANDS = [Command.ON, Command.OFF, Command.LEVEL, Command.PREVIOUS,
                Command.TOGGLE, Command.AUTOMATIC, Command.MANUAL, Command.INITIAL, Command.STATUS]
    
    def __init__(self, *args, **kwargs):
        self._command_lock = thread.allocate_lock()
        super(StateDevice, self).__init__(*args, **kwargs)
        if not kwargs.get('devices', None) and len(args)>0:
            kwargs.update({'devices': args[0]})
        self._initial_vars(*args, **kwargs)
        self._process_kwargs(kwargs)
        self._initial_from_devices(*args, **kwargs)
        if not self.state or self.state == State.UNKNOWN:
            self.command(Command.INITIAL, source=self)

    def _initial_vars(self, *args, **kwargs):
        self._state = State.UNKNOWN
        self._previous_state = self._state
        self._previous_command = None
        self._last_set = datetime.now()
        self._changes_only = False
        self._delegates = []
        self._times = []
        self._maps = {}
        self._delays = {}
        self._delay_timers = {}
        self._triggers = {}
        self._trigger_timers = {}
        self._ignores = {}
        self._restrictions = {}
        self._idle_timer = {}
        self._idle_command = None
        self._devices = []
        self._automatic = True
        self._retrigger_delay = None
#        self.invert(False)
        
        
    def invert(self, *args, **karwgs):
        if not self._maps.get((Command.ON, None), None):
            if args[0]:
                self.mapped(command=Command.ON, mapped=Command.OFF)
            else:
                self.mapped(command=Command.ON, mapped=Command.ON)
        if not self._maps.get((Command.OFF, None), None):
            if args[0]:
                self.mapped(command=Command.OFF, mapped=Command.ON)
            else:
                self.mapped(command=Command.OFF, mapped=Command.OFF)
        
    @property
    def state(self):
        return self._get_state()

    @state.setter
    def state(self, value, *args, **kwargs):
        return self._set_state(value, *args, **kwargs)

    def _get_state(self):
        return self._state
    
    def set_state(self, value, *args, **kwargs):
        return self._set_state(value, *args, **kwargs)
    
    def _set_state(self, value, *args, **kwargs):
        source = kwargs.get('source', None)
        if value != self._state:
            self._previous_state = self._state
        self._last_set = datetime.now()
        self._state = value
        return self._state
    
    def __getattr__(self, name):
        # Give this object methods for each command supported
        if self._is_valid_command(name):
            return lambda *a, **k: self.command(name, *a, sub_state=a, **k)

    def command(self, command, *args, **kwargs):
        # Lets process one command at a time please
        with self._command_lock:
            source = kwargs.get('source', None)
            source_property = kwargs.get('source_property', None)
#             if source_property == Property.DELAY:
#                 pass
#             if source_property == Property.IDLE:
#                 pass
#             if source_property == None:
#                 pass
            if not self._is_ignored(command, source):
                m_command = self._process_maps(*args, command=command, **kwargs)
                if m_command != command:
                    self._logger.debug("{name} Map from '{command}' to '{m_command}'".format(
                                                                            name=self.name,
                                                                            command=command,
                                                                            m_command=m_command,
                                                                                             ))

                (state, map_command) = self._command_state_map(m_command, *args, **kwargs)

                if map_command == Command.MANUAL:
                    self._automatic = False
                elif map_command == Command.AUTOMATIC:
                    self._automatic = True
                
                if self._is_restricted(map_command, source):
                    state = None
                    map_command = None
        
                if state and map_command and self._is_valid_state(state):
                    if not self._filter_retrigger_delay(command=map_command, source=source, new_state=state, original_state=self.state, original=command):
                    
                        if source == self or (not self._get_delay(map_command, source, original=command) or not self._automatic):
                            original_state = self.state
                            self._logger.info('{name} changed state from "{original_state}" to "{state}", by command {command} from {source}'.format(
                                                              name=self.name,
                                                              state=state,
                                                              original_state=original_state,
                                                              command=map_command,
                                                              source=source.name if source else None,
                                                                                                                          ))
                            self._set_state(state, source=source)
                            self._cancel_delays(map_command, source, original=command, source_property=source_property)
                            if self._automatic:
                                self._idle_start(command=map_command, source=source, original_command=command)
                            self._previous_command = map_command
                            self._delegate_command(map_command, original_state=original_state, *args, **kwargs)
                            if self._automatic:
                                self._trigger_start(map_command, source, original=command)
                            self._logger.debug('{name} Garbarge Collection queue:{queue}'.format(
                                                                                        name=self.name,
                                                                                        queue=str(StateDevice.dump_garbage()),
                                                                                                 ))
                        else:
                            self._logger.debug("{name} command {command} from {source} was delayed".format(
                                                                                                       name=self.name,
                                                                                                       command=command,
                                                                                                       source=source.name if source else None
                                                                                                       ))
                            self._delay_start(map_command, source, original=command)
                    else:
                        # retrigger
                        self._logger.debug("{name} Retrigger delay ignored command {command} from {source}".format(
                                                                                               name=self.name,
                                                                                               command=command,
                                                                                               source=source.name if source else None
                                                                                               ))
                elif command == Command.STATUS:
                    # If this is a status request, dont set state just pass along the command.
                    self._logger.debug("{name} delgating 'Status' command from {source}".format(
                                                                                               name=self.name,
                                                                                               command=command,
                                                                                               source=source.name if source else None
                                                                                               ))
                    self._delegate_command(command, original_state=self.state, *args, **kwargs)
                else:
                    self._logger.debug("{name} mapped to nothing, ignored command {command} from {source}".format(
                                                                                               name=self.name,
                                                                                               command=command,
                                                                                               source=source.name if source else None
                                                                                               ))
            else:
                self._logger.debug("{name} ignored command {command} from {source}".format(
                                                                                           name=self.name,
                                                                                           command=command,
                                                                                           source=source.name if source else None
                                                                                           ))

    def _command_state_map(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        state = None
        state = self._command_to_state(command, state)
        m_command = self._state_to_command(state, command)
        if command == Command.LEVEL or (isinstance(command, tuple) and command[0] == Command.LEVEL):
            if isinstance(command, tuple):
                state = (State.LEVEL, command[1:])
                if len(command[1:]) > 1:
                    state = sum([(State.LEVEL, ), command[1:]], ())
                else:
                    state = (State.LEVEL, command[1])
#                m_command = command
            else:
                state = (State.LEVEL, kwargs.get('sub_state', (0,))[0])
#                m_command = (Command.LEVEL,  kwargs.get('sub_state', (0,) ))
            m_command = self._state_to_command(state, m_command)
        elif command == Command.SETPOINT or (isinstance(command, tuple) and command[0] == Command.SETPOINT):
            if isinstance(command, tuple):
                state = (State.SETPOINT, command[1:])
                if len(command[1:]) > 1:
                    state = sum([(State.SETPOINT, ), command[1:]], ())
                else:
                    state = (State.SETPOINT, command[1])
#                m_command = command
            else:
                state = (State.SETPOINT, kwargs.get('sub_state', (0,))[0])
        elif isinstance(command, tuple) and self._is_valid_command(command[0]) and command[0] != Command.LEVEL:
            m_command = command
            state = self._previous_state
        elif command == Command.PREVIOUS:
            state = self._previous_state
            m_command = self._state_to_command(state, m_command)            
        elif command == Command.TOGGLE:
            state = self.toggle_state()
            m_command = self._state_to_command(state, m_command)
        elif command == Command.INITIAL:
            state = self.state
        elif command == Command.AUTOMATIC or command == Command.MANUAL:
            m_command = command
        return (state, m_command)

    def toggle_state(self):
        if self.state == State.ON:
            state = State.OFF
        else:
            state = State.ON
        return state
    
    def _command_to_state(self, command, state):
        # Try to map the same state ID
        try:
#            state = getattr(State, command)
            primary = command
            if isinstance(command, tuple):
                primary = command[0]
            for attribute in dir(State):
                if getattr(State, attribute) == primary:
                    return command
        except Exception, ex:
            self._logger.debug("{name} Could not find command to state for {command}".format(
                                                                            name=self.name,
                                                                            command=command,                                                                                                                 
                                                                            ))
        return state
    
    def _state_to_command(self, state, command):
        try:
#            return Command['state']
            primary = state
            if isinstance(state, tuple):
                primary = state[0]
            for attribute in dir(Command):
                if getattr(Command, attribute) == primary:
                    return state
            return command
        except Exception, ex:
            self._logger.debug("{name} could not map state {state} to command".format(
                                                                        name=self.name,
                                                                        state=state,
                                                                                                    ))
            return command
    
    def _process_kwargs(self, kwargs):
        # Process each initializing attribute as a method call on this object
        # devices have priority
        if kwargs.get('devices', None):
            try:
                getattr(self, 'devices')( **kwargs['devices'])
            except Exception, ex:
                getattr(self, 'devices')( kwargs['devices'])

        # run through the rest
        for k, v in kwargs.iteritems():
            if k.lower() != 'devices':
                attribute = getattr(self, k)
                if not attribute:
                    self._logger.error('Keyword: "{0}" not found in object construction.'.format(k))
                else:
                    try:
                        attribute(**v)
                    except ValueError, ex:
                        raise ex
                    except Exception, ex:
                        if callable(attribute):
                            if isinstance(v, tuple):
                                for v1 in v:
                                    try:
                                        attribute(**v1)
                                    except Exception, ex:
                                        attribute(v1)
                            else:
                                    attribute(v)
                        else:
                            attribute = v
                
            
    def _process_maps(self, *args, **kwargs):
        source = kwargs.get(Attribute.SOURCE, None)
        command = kwargs.get(Attribute.COMMAND, None)
        mapped = None

        self._logger.debug("{name} MAPS dump: {maps}".format(
                                                name=self.name,
                                                maps=str(self._maps),
                                                            ))

        for (c, s), (target, timer) in self._maps.iteritems():
            commands = []
            sources = []
            if isinstance(s, tuple):
                sources = s
            else:
                sources = (s, )
            if isinstance(c, tuple):
                commands = c
            else:
                commands = (c, )
            
            # Find specific first
            if command in commands and source in sources:
                if not timer or not self._automatic:
                    return target
                else:
                    self._logger.debug('{name} Map Timer Started for command "{command}" from source "{source}" will send "{target}" in "{secs}" secs.'.format(
                                            name=self.name,
                                            source=source.name if source else None,
                                            command=command,
                                            target=target,
                                            secs=timer.interval,
                    ))
                    timer.action(self.command, (target, ), source=self, original=source)
                    timer.restart()
                    return None

            # Go for a more general match next
            if command in commands and None in sources:
                if not timer or not self._automatic:
                    return target
                else:
                    self._logger.debug('{name} Map Timer Started for command "{command}" from source "{source}" will send "{target}" in "{secs}" secs.'.format(
                                            name=self.name,
                                            source=source,
                                            command=command,
                                            target=target,
                                            secs=timer.interval,
                    ))
                    timer.action(self.command, (target, ), source=self, original=source)
                    timer.restart()
                    return None

        
        return command
 
    def _is_valid_state(self, state):
        isFound = state in self.STATES
        if not isFound:
            try:
                isFound = state[0] in self.STATES
            except:
                pass
        if not isFound:
            self._logger.debug("{name} tried to be set to invalid state {state}".format(
                                                                        name=self.name,
                                                                        state=state,
                                                                                        ))
        return isFound

    def _is_valid_command(self, command):
        return command in self.COMMANDS

    def initial(self, state):
        try: # Check to see if this is a device reference
            last_command = state.last_command
            self.command(last_command, source=state)
#            (m_state, m_command) = self._command_state_map(last_command)
#            self.state = m_state
        except: # Just a value
#            self.state = state
            self.command(self._state_to_command(state, None), source=None)
        
    def time(self, *args, **kwargs):
        # time, command
        times = kwargs.get('time', None)
        command = kwargs.get('command', State.UNKNOWN)
        
        if times:
            if not isinstance( times, tuple) or (isinstance(times, tuple) and isinstance(times[0], (long, int))):
                times = (times, )
            for time in times:
                timer = CronTimer()
                if isinstance(time, tuple):
                    timer.interval(*time)
                else:
                    timer.interval(*CronTimer.to_cron(time))
                timer.action(self.command, (command))
                timer.start()
                self._times.append((command, timer))

    def on_command(self, device=None, remove=False):
        if not remove:
            self._delegates.append(device)
        else:
            self._delegates.remove(device)
    
    def _delegate_command(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        original_state = kwargs.get('original_state', None)
        
        for delegate in self._delegates:
#            print "here {name} s:{source} d:{delegate}".format(
#                                                               name=self.name,
#                                                               source=source.name if source else None,
#                                                               delegate=delegate.name if delegate else None,
#                                                               )
            if delegate != self and source != delegate and \
                (not self._changes_only or \
                (self._changes_only and self._state != original_state)):
                self._logger.debug("{name} delegating command {command} from {source} to object {delegate}".format(
                                                                                   name=self.name,
                                                                                   command=command,
                                                                                   source=source.name if source else None,
                                                                                   delegate=delegate.name,
                                                                           ))
                delegate.command(command=command, source=self)
            else:
                self._logger.debug("{name} Avoid duplicate delegation of {command} from {source} to object {delegate}".format(
                                                                                   name=self.name,
                                                                                   command=command,
                                                                                   source=source.name if source else None,
                                                                                   delegate=delegate.name,
                                                                           ))
                
    def devices(self, *args, **kwargs):
        devices = args[0]

        if not isinstance(devices, tuple):
            devices = (devices, )
                   
        for device in devices:
            if device:
                self._add_device(device)

    def add_device(self, device):
        return self._add_device(device)

    def _add_device(self, device):
        if not isinstance(device, dict):
            self._devices.append(device)
            self._logger.debug("{name} added new device {device}".format(
                                                                         name=self.name,
                                                                         device=device.name,
                                                                         ))
            return device.on_command(device=self)
        return True

    def remove_device(self, device):
        if device in self._devices:
            device.on_command(device=self, remove=True)
            self._devices.remove(device)
            return True
        else:
            return False
    
    def mapped(self, *args, **kwargs):
        command = kwargs.get('command', None)
        mapped = kwargs.get('mapped', None)
        source = kwargs.get('source', None)
        secs = kwargs.get('secs', None)
        timer = None
        commands = command
        if not isinstance(command, tuple):
            commands = (command, )
        for c in commands:
            if secs:
                timer = CTimer()
                timer.interval = secs
                timer.action(self.command, (mapped, ), source=self, original=source)
    #        self._maps.append({'command': command, 'mapped': mapped, 'source': source})
            sources = source
            if not isinstance(source, tuple):
                sources = (source ,)
            for s in sources:
                self._maps.update({(c, s): (mapped, timer)}) 
            
    def delay(self, *args, **kwargs):
        commands = kwargs.get('command', None)
        if (not isinstance(commands, tuple)):
            commands = (commands, )
        mapped = kwargs.get('mapped', None)
        sources = kwargs.get('source', None)
        if (not isinstance(sources, tuple)):
            sources = (sources, )
        secs = kwargs.get('secs', None)
        
        for command in commands:
            for source in sources:
                if not mapped:
                    m = command
                else:
                    m = mapped
                timer = CTimer()
                timer.interval=secs
                timer.action(self.command, (m, ), source=self, original=source, source_property=Property.DELAY)
                self._delays.update({(command, source): {'mapped': m, 'secs': secs, 'timer': timer}})
        return True

    def _get_delay(self, command, source, original=None, include_zero=False):
        delay = self._delays.get((command, source), None)
        if not delay and original:
            delay = self._delays.get((original, source), None)
        if delay:
            if delay['secs'] > 0 or include_zero:
                return delay
            else:
                return None
        
        delay = self._delays.get((command, None), None)
        if not delay and original:
            delay = self._delays.get((original, None), None)
        if delay and (delay['secs'] > 0 or include_zero):
            return delay

        return None       
    
    def _cancel_delays(self, command, source, original=None, source_property=None):
        if not self._get_delay(command, source, original) and source_property != Property.IDLE:
            for c, timer in self._delay_timers.iteritems():
                self._logger.debug("{name} stopping an existing delay timer of '{interval}' secs for command: '{command}' because the same non-delayed command was now processed. From {source} original command {original}".format(
                                                                                           name=self.name,
                                                                                           command=command,
                                                                                           source=source.name if source else None,
                                                                                           interval=timer.interval,
                                                                                           original=original,
                                                                                           ))
                timer.stop()

    def _delay_start(self, command, source, *args, **kwargs):
        original_command = kwargs.get('original', None)
        delay = self._get_delay(command, source, original_command, include_zero=True)
        if delay:
            timer = self._delay_timers.get(delay['mapped'], None)
            if not timer:
                timer = CTimer()
            timer.stop()
            if delay['secs'] > 0:
                timer.action(self.command, (delay['mapped'], ), source=self, original=source, source_property=Property.DELAY)
                timer.interval = delay['secs']
                self._delay_timers.update({delay['mapped']: timer} )
                timer.start()
                self._logger.debug('{name} command "{command}" from source "{source}" delayed, mapped to "{mapped}" waiting {secs} secs. '.format(
                                                                                      name=self.name,
                                                                                      source=source.name if source else None,
                                                                                      command=command,
                                                                                      mapped=delay['mapped'],
                                                                                      secs=delay['secs'],
                                                                                ))

    @property
    def idle_time(self):
        difference = datetime.now() - self._last_set
        return difference.total_seconds()

    def idle(self, *args, **kwargs):
        command = kwargs.get('command', None)
        source = kwargs.get('source', None)
        mapped = kwargs.get(Attribute.MAPPED, None)
        secs = kwargs.get('secs', None)
        if secs:
            timer = CTimer()
            timer.interval = secs
            timer.action(self.command, (mapped, ), source=self, original=source, source_property=Property.IDLE)
#            self._idle_timer = timer
            self._idle_timer.update({(command, source): {Attribute.SECS: secs, 
                                                         Attribute.MAPPED: mapped,
                                                         'timer': timer}})
            
    def _idle_start(self, *args, **kwargs):
        command = kwargs.get('command', None)
        source = kwargs.get('source', None)
        original_command = kwargs.get('original_command', None)
        idle = self._idle_timer.get((command, source), None)
        if not idle:
            idle = self._idle_timer.get((original_command, source), None)
        if not idle:
            idle = self._idle_timer.get((None, source), None)
        if not idle:
            idle = self._idle_timer.get((Command, None), None)
        if not idle:
            idle = self._idle_timer.get((None, None), None)
        if idle:
            if idle[Attribute.MAPPED] and source != self and self.state != State.OFF:
                timer = idle['timer']
                timer.action(self.command, (idle[Attribute.MAPPED], ), source=self, original=source, source_property=Property.IDLE)
                timer.start()
        
        
    def ignore(self, *args, **kwargs):
        commands = kwargs.get('command', None)
        sources = kwargs.get('source', None)
        start = kwargs.get(Attribute.START, None)
        end = kwargs.get(Attribute.END, None)

        if not isinstance(commands, tuple):
            commands = (commands, )
        if not isinstance(sources, tuple):
            sources = (sources, )

        for command in commands:
            for source in sources:
                self._ignores.update({
                                      (command, source): {
                                                          Attribute.START: CronTimer.to_cron(start),
                                                         Attribute.END: CronTimer.to_cron(end),
                                                     }
                                      })
                self._logger.debug("{name} add ignore for {command} from {source}".format(
        										name=self.name,
        										command=command,
        										source=source.name if source else None,
        										));
        
    def _is_ignored(self, command, source):
        is_ignored = False
        self._logger.debug("{name} check ignore for {command} from {source}".format(
                                        name=self.name,
                                        command=command,
                                        source=source.name if source else None,
                                        ));

        
        match = self._match_condition(command, source, self._ignores)
        if match:
            return True
        else:
            return False
        

    def restriction(self, *args, **kwargs):
        states = kwargs.get(Attribute.STATE, None)
        sources = kwargs.get(Attribute.SOURCE, None)
        targets = kwargs.get(Attribute.TARGET, None)
        start = kwargs.get(Attribute.START, None)
        end = kwargs.get(Attribute.END, None)

        if not isinstance(states, tuple):
            states = (states, )
        if not isinstance(sources, tuple):
            sources = (sources, )
        if not isinstance(targets, tuple):
            targets = (targets, )
        
        for state in states:
            for source in sources:
                for target in targets:
                    self._restrictions.update({
                                          (state, source, target): {
                                                              Attribute.START: CronTimer.to_cron(start),
                                                             Attribute.END: CronTimer.to_cron(end),
                                                         }
                                          })
                    self._logger.debug("{name} add restriction for {state} from {source} on {target}".format(
                                                    name=self.name,
                                                    state=state,
                                                    target=target,
                                                    source=source.name if source else None,
                                                    ));

    def _is_restricted(self, command, source):
        if self._restrictions and source != self:
            for state, source, target in self._restrictions:
                c_state = source.state
                if (state == c_state and (target==None or target==command)):
                    if (self._match_condition_item(self._restrictions.get((state, source, target)))):
                        self._logger.debug("{name} Restricted. ignoring".format(
                                                                             name=self.name,
                                                                             ))
                        return True

        return False
    
    def _match_condition(self, command, source, conditions):
        # Specific match first
        cond = self._match_condition_item(self._get_condition(command, source, conditions))
        if cond:
            return cond
        cond = self._match_condition_item(self._get_condition(command, None, conditions))
        if cond:
            return cond
        cond = self._match_condition_item(self._get_condition(None, source, conditions))
        if cond:
            return cond
        cond = self._match_condition_item(self._get_condition(None, None, conditions))
        if cond:
            return cond
        
    def _get_condition(self, command, source, conditions):
        result = conditions.get((command, source), None)

        if not result: # Check for substate matches as well (Command.LEVEL, etc)
            if isinstance(command, tuple):
                result = conditions.get((command[0], source), None)
        return result
                    
    
    def _match_condition_item(self, item):
        if not item:
            return None

        start = item.get(Attribute.START, None)
        if start:
            end = item.get(Attribute.END, None)
            if end:
                now = datetime.now().timetuple()[3:6]
                now_cron = CronTimer.to_cron("{h}:{m}:{s}".format(
                                                                  h=now[0],
                                                                  m=now[1],
                                                                  s=now[2],
                                                                  ))
                result = crontime_in_range(now_cron, start, end)
                self._logger.debug("Compare Time Range:("+ str(result) +")->" + str(now_cron) +"-" + str(start) + "-"+ str(end))
                return result 
        return item

    def trigger(self, *args, **kwargs):
        commands = kwargs.get(Attribute.COMMAND, None)
        sources = kwargs.get(Attribute.SOURCE, None)
        mapped = kwargs.get(Attribute.MAPPED, None)
        secs = kwargs.get(Attribute.SECS, None)
        start = kwargs.get(Attribute.START, None)
        end = kwargs.get(Attribute.END, None)
        
        if not isinstance(commands, tuple):
            commands = (commands, )
        if not isinstance(sources, tuple):
            sources = (sources, )
        
        for command in commands:
            for source in sources:
                m = None
                if not mapped:
                    m = command
                else:
                    m = mapped
                self._triggers.update({(command, source): {Attribute.SECS: secs, 
                                                           Attribute.MAPPED: m,
                                                           Attribute.START: CronTimer.to_cron(start),
                                                           Attribute.END: CronTimer.to_cron(end),
                                                           }})
        
#        timer = CTimer()
#        timer.interval=secs
#        timer.action(self.command, (mapped, ), source=self, original=source)
#        self._triggers.append({'command': command, 'mapped': mapped, 'source': source, 'secs': secs, 'timer': timer})

    def _trigger_start(self, command, source, *args, **kwargs):
        original_command = kwargs.get('original', None)
        trigger = self._triggers.get((command, source), None)
        if not trigger and original_command:
            trigger = self._triggers.get((original_command, source), None)
        if not trigger:
            trigger = self._triggers.get((command, None), None)
        if not trigger:
            trigger = self._triggers.get((original_command, None), None)
##       trigger = self._match_condition(command, source, self._triggers)
        
        if trigger and self._match_condition_item(trigger):
            timer = self._trigger_timers.get(trigger[Attribute.MAPPED], None)
            if not timer:
                timer = CTimer()
            timer.stop()
            if trigger[Attribute.SECS] > 0:
                timer.action(self.command, (trigger[Attribute.MAPPED], ), source=self, original=source)
                timer.interval = trigger[Attribute.SECS]
                self._trigger_timers.update({trigger[Attribute.MAPPED]: timer} )
                timer.start()
                self._logger.debug('{name} command "{command}" from source "{source}" trigger started, mapped to "{mapped}" waiting {secs} secs. '.format(
                                                                                      name=self.name,
                                                                                      source=source.name if source else None,
                                                                                      command=command,
                                                                                      mapped=trigger[Attribute.MAPPED],
                                                                                      secs=trigger[Attribute.SECS],
                                                                                ))  
            
        
#        for trigger in self._triggers:
#            if trigger['command'] == command and \
#            (not trigger['source'] or trigger['source'] == source):
#                trigger['timer'].action(self.command, (trigger['mapped'], ), source=self, original=source)
#                trigger['timer'].start()
                
    def _initial_from_devices(self, *args, **kwargs):
        state = None
        if self.state == State.UNKNOWN:
            for device in self._devices:
#                state = device.state
                (state, command) =  self._command_state_map(device.last_command)
                if state:
                    self.initial(device)
                    self._logger.debug("{name} initial for {command} from {state}".format(
        										name=self.name,
        										command=command,
        										state=state,
        										));
        return
    
    @property
    def last_command(self):
        return self._previous_command
    
    def changes_only(self, value):
        self._changes_only=value
        return self._changes_only
    
    def retrigger_delay(self, *args, **kwargs):
        secs = kwargs.get('secs', None)
        self._retrigger_delay = CTimer()
        self._retrigger_delay.interval = secs       

    def _filter_retrigger_delay(self, *args, **kwargs):
        """
        If there is a need to squelch multiple of the same command within a certain timeframe
        """
        command = kwargs.get('command', None)
        original_state = kwargs.get('original_state', None)
        new_state = kwargs.get('new_state', None)
        if new_state == original_state and self._retrigger_delay and self._retrigger_delay.isAlive():
            return True
        elif new_state != original_state and self._retrigger_delay:
            self._retrigger_delay.restart()
        return False          

    @staticmethod
    def dump_garbage():
        """
        show us what's the garbage about
        """
        c=-1
        # force collection
    #    print "\nGARBAGE:"
        gc.collect()
    
    #    print "\nGARBAGE OBJECTS:"
#        for x in gc.garbage:
#            s = str(x)
#            if len(s) > 80: s = s[:80]
#            print type(x),"\n  ", s
        try:
            c = len(gc.garbage)
        except:
            pass
        return c
