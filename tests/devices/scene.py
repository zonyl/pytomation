from mock import Mock
from unittest import TestCase

from pytomation.devices import Scene2, Interface2Device, State2Device, State2

class SceneDeviceTests(TestCase):
    def test_instantiation(self):
        scene = Scene2()
        self.assertIsNotNone(scene)
        
    def test_scene_activate(self):
        interface = Mock()
        interface.onCommand.return_value = True
        
        d1 = Interface2Device('d1', interface)
        d2 = Interface2Device('d2', interface)

        scene = Scene2(
                      address='s1',
                      devices= (interface,
                                {d1: {
                                     'state': State2.ON,
                                     'rate': 10,
                                     },
                                d2: {
                                     'state': (State2.LEVEL, 30),
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
                                                                         'state': State2.ON,
                                                                         'rate': 10,
                                                                         },
                                                                    d2: {
                                                                         'state': (State2.LEVEL, 30),
                                                                         'rate': 10,
                                                                         },
                                                                    },
                                                           )
