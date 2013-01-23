from unittest import TestCase, main
from mock import Mock

from pytomation.common.pytomation_system import *
from pytomation.interfaces import HAInterface
from pytomation.devices import StateDevice


class SystemTests(TestCase):
    def test_get_instances(self):
        mint = Mock()
        mint.read.return_value = ''
        before = get_instances()
        int = HAInterface(mint, name='Int1')
        dev = StateDevice(name='Dev1')
        a = get_instances()
        self.assertIsNotNone(a)
        self.assertEqual(len(a), len(before))
        
    def test_get_instances_detail(self):
        l = len(get_instances())
        mint = Mock()
        mint.read.return_value = ''
        int = HAInterface(mint, name='Int1')
        dev = StateDevice(name='Dev1')
        a = get_instances_detail()
        self.assertIsNotNone(a)
        self.assertEqual(len(a), l+2)
        self.assertEqual(a[dev.type_id]['name'], 'Dev1')
        self.assertEqual(a[dev.type_id]['type_name'], 'StateDevice')
        
