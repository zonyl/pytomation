from unittest import TestCase

from pytomation.devices import Room, Motion, Light, StateDevice, State

class RoomTests(TestCase):
    def setUp(self):
        pass
    
    def test_init(self):
        r = Room()
        self.assertIsNotNone(r)
        
    def test_room_occupied(self):
        m = Motion()
        r = Room(devices=m)
        r.vacate()
        self.assertEqual(r.state, State.VACANT)
        m.motion()
        self.assertEqual(r.state, State.OCCUPIED)
        
    def test_room_to_room_vacate(self):
        m1 = Motion(name='m1')
        m2 = Motion(name='m2')
        m3 = Motion(name='m3')
        r1 = Room(name='r1', devices=m1)
        r2 = Room(name='r2', devices=(m2, r1))
        r3 = Room(name='r3', devices=(m3, r2))
        r1.add_device(r2)
        r2.add_device(r3)

        m1.motion()
        self.assertEqual(r1.state, State.OCCUPIED)
        self.assertEqual(r2.state, State.VACANT)
        self.assertEqual(r3.state, State.UNKNOWN)
        m2.motion()
        self.assertEqual(r1.state, State.VACANT)
        self.assertEqual(r2.state, State.OCCUPIED)
        self.assertEqual(r3.state, State.VACANT)
        m3.motion()
        self.assertEqual(r1.state, State.VACANT)
        self.assertEqual(r2.state, State.VACANT)
        self.assertEqual(r3.state, State.OCCUPIED)
        m1.motion()
        self.assertEqual(r1.state, State.OCCUPIED)
        self.assertEqual(r2.state, State.VACANT)
        self.assertEqual(r3.state, State.OCCUPIED)
        m2.motion()
        self.assertEqual(r1.state, State.VACANT)
        self.assertEqual(r2.state, State.OCCUPIED)
        self.assertEqual(r3.state, State.VACANT)
        
        