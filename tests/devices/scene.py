from mock import Mock
from unittest import TestCase

from pytomation.devices import Scene, InterfaceDevice, StateDevice, State

class SceneDeviceTests(TestCase):
    def test_instantiation(self):
        scene = Scene()
        self.assertIsNotNone(scene)
        
    def test_scene_activate(self):
        interface = Mock()
        interface.onCommand.return_value = True
        
        d1 = InterfaceDevice('d1', interface)
        d2 = InterfaceDevice('d2', interface)

        scene = Scene(
                      address='s1',
                      devices= (interface,
                                {d1: {
                                     'state': State.ON,
                                     'rate': 10,
                                     },
                                d2: {
                                     'state': (State.LEVEL, 30),
                                     'rate': 10,
                                     },
                                }),
                      update=True,
                      )
        self.assertIsNotNone(scene)
        scene.activate()
        
        self.assertTrue(interface.update_scene.called)
        self.assertTrue(interface.activate.called)
        
        interface.update_scene.assert_called_with(
                                                           's1',
                                                          devices= {d1: {
                                                                         'state': State.ON,
                                                                         'rate': 10,
                                                                         },
                                                                    d2: {
                                                                         'state': (State.LEVEL, 30),
                                                                         'rate': 10,
                                                                         },
                                                                    },
                                                           )
