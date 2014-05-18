import select
import time

from unittest import TestCase, main
from mock import Mock
from tests.common import MockInterface
from pytomation.interfaces import Bv4626, Serial, HACommand
from pytomation.devices import State

class Bv4626Tests(TestCase):
    useMock = True

    def setUp(self):
        self.ms = MockInterface()
        if self.useMock:  # Use Mock Serial Port
            self.byvac = Bv4626(self.ms, outputs='abefh')
            self.ms.add_response({'\015': '*'})
            self.ms.add_response({'\033[76s': self.byvac.ACK})
        else:
            self.serial = Serial('/dev/ttyUSB0', 115200, rtscts=True)
            self.byvac = Bv4626(self.serial, outputs='abefh')

    def tearDown(self):
        self.byvac.shutdown()
        self.serial = None

    def test_instantiation(self):
        self.assertIsNotNone(self.byvac,
                             'BV4626 interface could not be instantiated')

    def test_b_get_device_id(self):
        # What will be written / what should we get back
        self.ms.add_response({'\033['+self.byvac._modemCommands['getDeviceId']: '4626'+self.byvac.ACK})

        response = self.byvac.getDeviceId()
        self.assertEqual(response, '4626')

    def test_d_get_firmware_version(self):
        # What will be written / what should we get back
        self.ms.add_response({'\033['+self.byvac._modemCommands['getFirmwareVersion']: '12'+self.byvac.ACK})

        response = self.byvac.getFirmwareVersion()
        self.assertEqual(response, '12')

    def test_a_relays(self):
        self.ms.add_response({'\033[' + self.byvac._modemCommands['turnOn'] + 'A': self.byvac.ACK})
        self.ms.add_response({'\033[' + self.byvac._modemCommands['turnOff'] + 'A': self.byvac.ACK})
        self.ms.add_response({'\033[' + self.byvac._modemCommands['turnOn'] + 'B': self.byvac.ACK})
        self.ms.add_response({'\033[' + self.byvac._modemCommands['turnOff'] + 'B': self.byvac.ACK})

        response = self.byvac.on('A')
        self.assertTrue(response)
        time.sleep(0.25)
        response = self.byvac.on('B')
        self.assertTrue(response)
        time.sleep(0.5)
        response = self.byvac.off('A')
        self.assertTrue(response)
        time.sleep(0.25)
        response = self.byvac.off('B')
        self.assertTrue(response)

        response = self.byvac.on('C')
        self.assertFalse(response)

    def test_c_outputs(self):
        self.ms.add_response({'\033[255a': self.byvac.ACK})
        self.ms.add_response({'\033[0a': self.byvac.ACK})
        self.ms.add_response({'\033[255h': self.byvac.ACK})
        self.ms.add_response({'\033[0h': self.byvac.ACK})

        response = self.byvac.on('a')
        self.assertTrue(response)
        time.sleep(0.25)
        response = self.byvac.on('h')
        self.assertTrue(response)
        time.sleep(0.5)
        response = self.byvac.off('a')
        self.assertTrue(response)
        time.sleep(0.25)
        response = self.byvac.off('h')
        self.assertTrue(response)

        response = self.byvac.on('c')
        self.assertFalse(response)

    #def test_device_status(self):
        #"""
        #UPBPIM, myPIM, 49, 0x1B08, 30
        #UPBD,   byvac_foyer,      myPIM,  49, 3
        #Response>  Foyer Light On
        #0000   50 55 30 38 31 30 33 31    PU081031
        #0008   30 33 31 45 32 32 36 34    031E2264
        #0010   31 30 0D                   10.
        #"""
        ##071031031E3067
        #self.ms.add_response({'\x14071031031E3067\x0D': 'PA\x0D'})
        ## Network / Device ID
        #response = self.byvac.status((49, 3))
        #self.assertTrue(response)

    #def test_update_status(self):
        #device = Mock()
        #device.address.return_value ='a1'
        #self.byvac.update_status();


    #def test_multiple_commands_at_same_time(self):
        #"""
        #Response>
        #0000   50 55 30 38 31 30 33 31    PU081031
        #0008   31 32 31 45 32 32 30 30    121E2200
        #0010   36 35 0D 50 55 30 38 31    65.PU081
        #0018   30 33 31 31 32 31 45 32    031121E2
        #0020   32 30 30 36 35 0D          20065.
        #"""
        
    #def test_incoming_on(self):
        #"""
        #UBP New: PU0804310006860037:0000   50 55 30 38 30 34 33 31    PU080431
        #0008   30 30 30 36 38 36 30 30    00068600
        #0010   33 37                      37
        
        #UBP New: PU0805310006860036:0000   50 55 30 38 30 35 33 31    PU080531
        #0008   30 30 30 36 38 36 30 30    00068600
        #0010   33 36                      36
        #"""
        #m_interface = Mock()
        #m_interface.read.return_value = ''
        #byvac = Bv4626(m_interface)
        #m_interface.callback.return_value = True
        #byvac.onCommand(address=(49,6), callback=m_interface.callback)
        #m_interface.read.return_value = 'PU0805310006860036'
##        time.sleep(4000)
        #time.sleep(2)
        #m_interface.callback.assert_called_with(address=(49,6), command=State.OFF, source=byvac)  
        #m_interface.read.return_value = ''

    #def test_incoming_link(self):
        #"""
        #UBP New Response: PU8A0431260F20FFFFFFEF
        #UPBN:49:15:38:20
        #"""
        #m_interface = Mock()
        #m_interface.callback.return_value = True
        #m_interface.read.return_value = ''
        #byvac = Bv4626(m_interface)
        #byvac.onCommand(address=(49,38,'L'), callback=m_interface.callback)
        #m_interface.read.return_value = 'PU8A0431260F20FFFFFFEF'
##        time.sleep(4000)
        #time.sleep(2)
        #m_interface.callback.assert_called_with(address=(49,38,'L'), command=State.ON, source=byvac)  
        #m_interface.read.return_value = ''
        
    #def test_incoming_k(self):
        #"""
#0000   50 55 30 37 31 34 31 36    PU071416
#0008   31 30 46 46 33 30 39 30    10FF3090
#0010   0D 50 55 30 37 31 35 31    .PU07151
#0018   36 31 30 46 46 33 30 38    610FF308
#0020   46 0D                      F.
        #"""
        #m_interface = Mock()
        #m_interface.callback.return_value = True
        #m_interface.read.return_value = ''
        #byvac = Bv4626(m_interface)
        #byvac.onCommand(address=(22,255), callback=m_interface.callback)
        #m_interface.read.return_value = "PU07141610FF3090\x0DPU07151610FF308F\x0D"
##        time.sleep(4000)
        #time.sleep(2)
        #m_interface.callback.assert_called_with(address=(22,255), command='status', source=byvac)  
        #m_interface.read.return_value = ''
            
        
    #def test_level(self):
        #response = self.byvac.l40((39, 4))
        #self.assertTrue(True)
        
    #def test_level2(self):
        #response = self.byvac.level((39, 4), 40)
        #self.assertTrue(True)

    #def test_link_activate(self):
        #"""
        #"""#        self.ms.add_response({'\x14081031031E226410\x0D': 'PA\x0D'})
        #self.ms.add_response({'\x14871031031E20F7\x0D': 'PA\x0D'})
        ## Network / Device ID 
        #response = self.byvac.on((49, 3, "L"))
        #self.assertTrue(response)

if __name__ == '__main__':
    main()
