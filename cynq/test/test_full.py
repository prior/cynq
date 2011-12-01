from .helper import TestCase
from cynq import Controller, VoodooStore, FacetStore, BaseSpec, Arm
#from pprint import pprint


class TestSpec1(BaseSpec):
    name = 'test1'
    rpushed = ('push1',)
    rpulled = ('pull',)
    shared = ('key','share')
    key = 'key'

class TestSpec2(BaseSpec):
    name = 'test2'
    rpushed = ('push2',)
    rpulled = ('pull',)
    shared = ('key','share')
    key = 'key'

#TODO: test api fail scenarios
#TODO: test local fail scenarios
#TODO: test snapshot fail scenarios


class FullTestCase(TestCase):
    def setUp(self):
        spec1 = TestSpec1()
        spec2 = TestSpec2()
        self.local = VoodooStore(pushgen=lambda dobj: 10)
        self.local1 = FacetStore(self.local)
        self.api1 = VoodooStore(pushgen=lambda dobj: 11)
        self.snapshot1 = VoodooStore()
        self.local2 = FacetStore(self.local)
        self.api2 = VoodooStore(pushgen=lambda dobj: 12)
        self.snapshot2 = VoodooStore()
        self.arm1 = Arm(spec1, self.api1,self.local1,self.snapshot1)
        self.arm2 = Arm(spec2, self.api2,self.local2,self.snapshot2)

    def tearDown(self):
        pass

    def test_one_arm_remote_create(self):
        expected = [{'key':1, 'push1':2, 'pull':10, 'share':4}]
        self.api1.ddata = [{'key':1, 'push1':2, 'pull':3, 'share':4}]
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,1,0,0),self.local1)
        self.assert_store(expected,(1,0,1,0),self.api1)
        self.assert_store(expected,(1,1,0,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_remote_create(self):
        expected1 = [{'key':1, 'push1':2, 'pull':10, 'share':4}]
        expected2 = [{'key':1, 'push2':12, 'pull':10, 'share':4}]
        self.api1.ddata = [{'key':1, 'push1':2, 'pull':3, 'share':4}]
        cynq = Controller(self.arm1, self.arm2).cynq()
        self.assert_store(expected1,(4,1,0,0),self.local1)
        self.assert_store(expected1,(1,0,1,0),self.api1)
        self.assert_store(expected1,(1,1,0,0),self.snapshot1)
        self.assert_store(expected2,(4,0,1,0),self.local2)
        self.assert_store(expected2,(1,1,0,0),self.api2)
        self.assert_store(expected2,(1,1,0,0),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_one_arm_local_create(self):
        expected = [{'key':1, 'push':11, 'pull':3, 'share':4}]
        self.local.ddata = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,0,1,0),self.local)
        self.assert_store(expected,(1,1,0,0),self.api1)
        self.assert_store(expected,(1,1,0,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_local_create(self):
        expected = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.local.ddata = expected
        cynq = Controller(self.arm1, self.arm2).cynq()
        self.assert_store(expected,(6,0,0,0),self.local)
        self.assert_store(expected,(1,1,0,0),self.api1)
        self.assert_store(expected,(1,1,0,0),self.snapshot1)
        self.assert_store(expected,(1,1,0,0),self.api2)
        self.assert_store(expected,(1,1,0,0),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_one_arm_local_delete(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.api1.ddata = seeds
        self.snapshot1.ddata = seeds
        expected = []
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,0,0,0),self.local)
        self.assert_store(expected,(1,0,0,1),self.api1)
        self.assert_store(expected,(1,0,0,1),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_local_delete(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.api1.ddata = seeds
        self.snapshot1.ddata = seeds
        self.api2.ddata = seeds
        self.snapshot2.ddata = seeds
        expected = []
        cynq = Controller(self.arm1, self.arm2).cynq()
        self.assert_store(expected,(6,0,0,0),self.local)
        self.assert_store(expected,(1,0,0,1),self.api1)
        self.assert_store(expected,(1,0,0,1),self.snapshot1)
        self.assert_store(expected,(1,0,0,1),self.api2)
        self.assert_store(expected,(1,0,0,1),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)
        
    def test_one_arm_remote_delete(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.local.ddata = seeds
        self.snapshot1.ddata = seeds
        expected = []
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,0,0,1),self.local)
        self.assert_store(expected,(1,0,0,0),self.api1)
        self.assert_store(expected,(1,0,0,1),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_remote_delete(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.local.ddata = seeds
        self.snapshot1.ddata = seeds
        self.snapshot2.ddata = seeds
        self.api2.ddata = seeds
        expected = []
        cynq = Controller(self.arm1, self.arm2).cynq()
        self.assert_store(expected,(6,0,0,1),self.local)
        self.assert_store(expected,(1,0,0,0),self.api1)
        self.assert_store(expected,(1,0,0,1),self.snapshot1)
        self.assert_store(expected,(1,0,0,1),self.api2)
        self.assert_store(expected,(1,0,0,1),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_one_arm_local_update(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.api1.ddata = seeds
        self.snapshot1.ddata = seeds
        expected = [{'key':1, 'push':2, 'pull':3, 'share':5}]
        self.local.ddata = expected
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,0,0,0),self.local)
        self.assert_store(expected,(1,0,1,0),self.api1)
        self.assert_store(expected,(1,0,1,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_local_update(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.api1.ddata = seeds
        self.snapshot1.ddata = seeds
        self.api2.ddata = seeds
        self.snapshot2.ddata = seeds
        expected = [{'key':1, 'push':2, 'pull':3, 'share':5}]
        self.local.ddata = expected
        cynq = Controller(self.arm1,self.arm2).cynq()
        self.assert_store(expected,(6,0,0,0),self.local)
        self.assert_store(expected,(1,0,1,0),self.api1)
        self.assert_store(expected,(1,0,1,0),self.snapshot1)
        self.assert_store(expected,(1,0,1,0),self.api2)
        self.assert_store(expected,(1,0,1,0),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)
       
    def test_one_arm_remote_update(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.local.ddata = seeds
        self.snapshot1.ddata = seeds
        expected = [{'key':1, 'push':2, 'pull':3, 'share':5}]
        self.api1.ddata = expected
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,0,1,0),self.local)
        self.assert_store(expected,(1,0,0,0),self.api1)
        self.assert_store(expected,(1,0,1,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_remote_update(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.local.ddata = seeds
        self.snapshot1.ddata = seeds
        self.api2.ddata = seeds
        self.snapshot2.ddata = seeds
        expected = [{'key':1, 'push':2, 'pull':3, 'share':5}]
        self.api1.ddata = expected
        cynq = Controller(self.arm1,self.arm2).cynq()
        self.assert_store(expected,(6,0,1,0),self.local)
        self.assert_store(expected,(1,0,0,0),self.api1)
        self.assert_store(expected,(1,0,1,0),self.snapshot1)
        self.assert_store(expected,(1,0,1,0),self.api2)
        self.assert_store(expected,(1,0,1,0),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_snapshot_recovery(self):
        seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.local.ddata = seeds
        expected = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.api1.ddata = expected
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,0,0,0),self.local)
        self.assert_store(expected,(1,0,0,0),self.api1)
        self.assert_store(expected,(1,1,0,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_initial_setup(self):
        expected = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.api1.ddata = expected
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,1,0,0),self.local)
        self.assert_store(expected,(1,0,0,0),self.api1)
        self.assert_store(expected,(1,1,0,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_one_arm_mixed_update(self):
        self.local.ddata = [{'key':1, 'push':2, 'pull':6, 'share':4}]
        self.snapshot1.ddata = [{'key':1, 'push':2, 'pull':3, 'share':4}]
        self.api1.ddata = [{'key':1, 'push':5, 'pull':3, 'share':4}]
        expected = [{'key':1, 'push':5, 'pull':6, 'share':4}]
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,0,1,0),self.local)
        self.assert_store(expected,(1,0,1,0),self.api1)
        self.assert_store(expected,(1,0,1,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)


    def test_one_arm_pushkey_local_create(self):
        class PushKeySpec(BaseSpec):
            name = 'pushkey'
            rpushed = ('key',)
            rpulled = ('pull',)
            shared = ('share',)
            key = 'key'

        spec = PushKeySpec()
        local = VoodooStore()
        api = VoodooStore(keygen=lambda dobj: 9)
        snapshot = VoodooStore()
        arm = Arm(spec, api, local, snapshot)
        local.ddata = [{'pull':3, 'share':4}]
        expected = [{'key':9, 'pull':3, 'share':4}]
        cynq = Controller(arm).cynq()
        self.assert_store(expected,(1,0,1,0),local)
        self.assert_store(expected,(1,1,0,0),api)
        self.assert_store(expected,(1,1,0,0),snapshot)
        self.assert_no_changes_on_another_cynq(cynq)


    def assert_no_changes_on_another_cynq(self, controller):
        for arm in controller.arms:
            for s in arm.stores:
                s._clear_stats()
                s._clear_cache()

        # make sure it's all equal to start
        arm_ddata = {}
        for arm in controller.arms:
            self.assert_equal_dlists(arm.api.ddata,arm.local.ddata)
            self.assert_equal_dlists(arm.api.ddata,arm.snapshot.ddata)
            self.assert_equal_dlists(arm.local.ddata,arm.snapshot.ddata)  # overkill just in case
            arm_ddata[arm] = arm.api.ddata

        controller.cynq()

        expected_local_reads = len(controller.arms)==1 and 1 or len(controller.arms)*4
        for arm in controller.arms:
            self.assert_store(arm_ddata[arm],(expected_local_reads,0,0,0),arm.local)
            self.assert_store(arm_ddata[arm],(1,0,0,0),arm.api)
            self.assert_store(arm_ddata[arm],(1,0,0,0),arm.snapshot)
            arm_ddata[arm] = arm.api.ddata


    def assert_store(self, *args):
        args = list(args)
        if len(args)==3: args[2:2]=[args[1]]  # if no post/pre disctinction, then just double up
        expected_ddata, expected_pre_stats, expected_post_stats, store = args
        self.assertEqual(expected_pre_stats, store.pre_stats)
        self.assertEqual(expected_post_stats, store.post_stats)
        self.assert_equal_dlists(expected_ddata, store.ddata)

