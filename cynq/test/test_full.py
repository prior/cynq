import helper
from cynq.controller import Controller
from cynq.store import VoodooMemoryStore
from copy import deepcopy
from cynq.spec import Spec
from cynq.arm import Arm
#from pprint import pprint

class TestSpec(Spec):
    name = 'test'
    rpushed = ('push',)
    rpulled = ('pull',)
    shared = ('key','share')
    key = 'key'

class TestCase(helper.TestCase):
    def setUp(self):
        spec = TestSpec()
        self.local = VoodooMemoryStore(spec)
        self.api1 = VoodooMemoryStore(spec)
        self.snapshot1 = VoodooMemoryStore(spec)
        self.api2 = VoodooMemoryStore(spec)
        self.snapshot2 = VoodooMemoryStore(spec)
        self.arm1 = Arm(self.api1,self.local,self.snapshot1)
        self.arm2 = Arm(self.api2,self.local,self.snapshot2)

    def tearDown(self):
        pass

    def test_one_arm(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.api1.ddata = deepcopy(seeds)
        cynq = Controller(self.arm1).cynq()
        self.assertEqual(((1,0,0,0),(1,0,0,0)),self.api1.stats)
        self.assert_equal_dlists(seeds, self.api1.ddata)
        self.assertEqual(((1,1,0,0),(1,1,0,0)),self.local.stats)
        self.assert_equal_dlists(seeds, self.local.ddata)
        self.assertEqual(((1,1,0,0),(1,1,0,0)),self.snapshot1.stats)
        self.assert_equal_dlists(seeds, self.snapshot1.ddata)
        self.assert_no_changes_on_another_cynq(cynq)


    def test
        # assert fine grained changes!
        # assert no changes on subsequent cynqs!

    def assert_no_changes_on_another_cynq(self, controller):
        for arm in self.arms()
        controller.clear_stats()


