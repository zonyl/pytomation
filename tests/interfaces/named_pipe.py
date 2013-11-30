import os, time

from unittest import TestCase

from pytomation.interfaces import NamedPipe, StateInterface
from pytomation.devices import StateDevice, State, Light

class NamedPipeTests(TestCase):
    def setUp(self):
        self._path_name = "/tmp/named_pipe_test"
        self.interface = NamedPipe(self._path_name)
            
    def test_instance(self):
        self.assertIsNotNone(self.interface)
    
    def test_pipe_read(self):
        test_message = 'Test'
        pipe = os.open(self._path_name, os.O_WRONLY)
        os.write(pipe, test_message)
        response = self.interface.read()
        self.assertEqual(test_message, response)
        
    def test_pipe_interface_read(self):
        path = '/tmp/named_pipe_test2'
        pi = StateInterface(NamedPipe(path))
        #pi.onCommand(self.test_pipe_interface_read_callback)
        d1 = Light(address=None, devices=pi)
        self.assertEqual(d1.state, State.UNKNOWN)

        pipe = os.open(path, os.O_WRONLY)
        os.write(pipe, State.ON)
        time.sleep(2)
        self.assertEqual(d1.state, State.ON)
        
    def test_pipe_interface_read_callback(self, *args, **kwargs):
        pass
        
        
    def tearDown(self):
        self.interface.close()
        