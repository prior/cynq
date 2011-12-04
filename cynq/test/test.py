from .helper import TestCase
from cynq import Controller, VoodooStore, FacetStore, BaseSpec, Arm
from .. import logging_helper
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
        self.local = VoodooStore(attrs=['push1','push2','pull','key','share','id'], key='id', push_attrs=['pull'], keygen=lambda dobj: 9, pushgen=lambda dobj: 10)
        self.local1 = FacetStore(self.local)
        self.api1 = VoodooStore(spec=spec1, pushgen=lambda dobj: 11)
        self.snapshot1 = VoodooStore(spec=spec1)
        self.local2 = FacetStore(self.local)
        self.api2 = VoodooStore(spec=spec2, pushgen=lambda dobj: 12)
        self.snapshot2 = VoodooStore(spec=spec2)
        self.arm1 = Arm(spec1, self.api1,self.local1,self.snapshot1)
        self.arm2 = Arm(spec2, self.api2,self.local2,self.snapshot2)
        self.log = logging_helper.get_log('cynq.test')

    def tearDown(self):
        pass

    def test_one_arm_remote_create(self):
        self.api1.ddata = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        expectedL = [{'id':9, 'key':1, 'share':4, 'pull':10, 'push1':2, 'push2':None}]
        expected1 = [{'key':1, 'share':4, 'pull':10, 'push1':2}]
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expectedL,(1,1,0,0),self.local)
        self.assert_store(expected1,(1,0,1,0),self.api1)
        self.assert_store(expected1,(1,1,0,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_remote_create(self):
        self.api1.ddata = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        expectedL = [{'id':9, 'key':1, 'share':4, 'pull':10, 'push1':2, 'push2':12}]
        expected1 = [{'key':1, 'share':4, 'pull':10, 'push1':2}]
        expected2 = [{'key':1, 'share':4, 'pull':10, 'push2':12}]
        cynq = Controller(self.arm1, self.arm2).cynq()
        self.assert_store(expectedL,(1,1,1,0),self.local)
        self.assert_store(expected1,(1,0,1,0),self.api1)
        self.assert_store(expected1,(1,1,0,0),self.snapshot1)
        self.assert_store(expected2,(1,1,0,0),self.api2)
        self.assert_store(expected2,(1,1,0,0),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_one_arm_local_create(self):
        self.local.ddata = [{'id':5, 'key':1, 'share':4, 'pull':3, 'push1':2, 'push2':None}]
        expectedL = [{'id':5, 'key':1, 'share':4, 'pull':3, 'push1':11, 'push2':None}]
        expected1 = [{'key':1, 'share':4, 'pull':3, 'push1':11}]
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expectedL,(1,0,1,0),self.local)
        self.assert_store(expected1,(1,1,0,0),self.api1)
        self.assert_store(expected1,(1,1,0,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_local_create(self):
        self.local.ddata = [{'id':5, 'key':1, 'share':4, 'pull':3, 'push1':2, 'push2':None}]
        expectedL = [{'id':5, 'key':1, 'share':4, 'pull':3, 'push1':11, 'push2':12}]
        expected1 = [{'key':1, 'share':4, 'pull':3, 'push1':11}]
        expected2 = [{'key':1, 'share':4, 'pull':3, 'push2':12}]
        cynq = Controller(self.arm1, self.arm2).cynq()
        self.assert_store(expectedL,(1,0,2,0),self.local)
        self.assert_store(expected1,(1,1,0,0),self.api1)
        self.assert_store(expected1,(1,1,0,0),self.snapshot1)
        self.assert_store(expected2,(1,1,0,0),self.api2)
        self.assert_store(expected2,(1,1,0,0),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_one_arm_local_delete(self):
        seeds = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        self.api1.ddata = seeds
        self.snapshot1.ddata = seeds
        expected = []
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,0,0,0),self.local)
        self.assert_store(expected,(1,0,0,1),self.api1)
        self.assert_store(expected,(1,0,0,1),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_local_delete(self):
        seeds = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        self.api1.ddata = seeds
        self.snapshot1.ddata = seeds
        self.api2.ddata = seeds
        self.snapshot2.ddata = seeds
        expected = []
        cynq = Controller(self.arm1, self.arm2).cynq()
        self.assert_store(expected,(1,0,0,0),self.local)
        self.assert_store(expected,(1,0,0,1),self.api1)
        self.assert_store(expected,(1,0,0,1),self.snapshot1)
        self.assert_store(expected,(1,0,0,1),self.api2)
        self.assert_store(expected,(1,0,0,1),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)
        
    def test_one_arm_remote_delete(self):
        self.local.ddata = [{'id':5, 'key':1, 'share':4, 'pull':3, 'push1':2, 'push2':None}]
        self.snapshot1.ddata = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        expected = []
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expected,(1,0,0,1),self.local)
        self.assert_store(expected,(1,0,0,0),self.api1)
        self.assert_store(expected,(1,0,0,1),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_remote_delete(self):
        self.local.ddata = [{'id':5, 'key':1, 'share':4, 'pull':3, 'push1':2, 'push2':None}]
        seeds = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        self.snapshot1.ddata = seeds
        self.snapshot2.ddata = seeds
        self.api2.ddata = seeds
        expected = []
        cynq = Controller(self.arm1, self.arm2).cynq()
        self.assert_store(expected,(1,0,0,1),self.local)
        self.assert_store(expected,(1,0,0,0),self.api1)
        self.assert_store(expected,(1,0,0,1),self.snapshot1)
        self.assert_store(expected,(1,0,0,1),self.api2)
        self.assert_store(expected,(1,0,0,1),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_one_arm_local_update(self):
        self.local.ddata = [{'id':5, 'key':1, 'share':6, 'pull':3, 'push1':2, 'push2':None}]
        seeds = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        self.api1.ddata = seeds
        self.snapshot1.ddata = seeds
        expectedL = [{'id':5, 'key':1, 'share':6, 'pull':3, 'push1':2, 'push2':None}]
        expected1 = [{'key':1, 'share':6, 'pull':3, 'push1':2}]
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expectedL,(1,0,0,0),self.local)
        self.assert_store(expected1,(1,0,1,0),self.api1)
        self.assert_store(expected1,(1,0,1,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_local_update(self):
        seeds1 = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        seeds2 = [{'key':1, 'share':4, 'pull':3, 'push2':None}]
        self.api1.ddata = seeds1
        self.snapshot1.ddata = seeds1
        self.api2.ddata = seeds2
        self.snapshot2.ddata = seeds2
        expectedL = [{'id':5, 'key':1, 'share':6, 'pull':3, 'push1':2, 'push2':None}]
        expected1 = [{'key':1, 'share':6, 'pull':3, 'push1':2}]
        expected2 = [{'key':1, 'share':6, 'pull':3, 'push2':None}]
        self.local.ddata = expectedL
        cynq = Controller(self.arm1,self.arm2).cynq()
        self.assert_store(expectedL,(1,0,0,0),self.local)
        self.assert_store(expected1,(1,0,1,0),self.api1)
        self.assert_store(expected1,(1,0,1,0),self.snapshot1)
        self.assert_store(expected2,(1,0,1,0),self.api2)
        self.assert_store(expected2,(1,0,1,0),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)
       
    def test_one_arm_remote_update(self):
        self.local.ddata = [{'id':5, 'key':1, 'share':4, 'pull':3, 'push1':2, 'push2':None}]
        self.snapshot1.ddata = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        expectedL = [{'id':5, 'key':1, 'share':6, 'pull':3, 'push1':2, 'push2':None}]
        expected1 = [{'key':1, 'share':6, 'pull':3, 'push1':2}]
        self.api1.ddata = expected1
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expectedL,(1,0,1,0),self.local)
        self.assert_store(expected1,(1,0,0,0),self.api1)
        self.assert_store(expected1,(1,0,1,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_two_arm_remote_update(self):
        self.local.ddata = [{'id':5, 'key':1, 'share':4, 'pull':3, 'push1':2, 'push2':None}]
        self.snapshot1.ddata = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        self.snapshot2.ddata = [{'key':1, 'share':4, 'pull':3, 'push2':None}]
        self.api1.ddata = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        self.api2.ddata = [{'key':1, 'share':6, 'pull':3, 'push2':None}]
        expectedL = [{'id':5, 'key':1, 'share':6, 'pull':3, 'push1':2, 'push2':None}]
        expected1 = [{'key':1, 'share':6, 'pull':3, 'push1':2}]
        expected2 = [{'key':1, 'share':6, 'pull':3, 'push2':None}]
        cynq = Controller(self.arm1,self.arm2).cynq()
        self.assert_store(expectedL,(1,0,1,0),self.local)
        self.assert_store(expected1,(1,0,1,0),self.api1)
        self.assert_store(expected1,(1,0,1,0),self.snapshot1)
        self.assert_store(expected2,(1,0,0,0),self.api2)
        self.assert_store(expected2,(1,0,1,0),self.snapshot2)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_snapshot_recovery(self):
        expectedL = [{'id':5, 'key':1, 'share':4, 'pull':3, 'push1':2, 'push2':None}]
        expected1 = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        self.local.ddata = expectedL
        self.api1.ddata = expected1
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expectedL,(1,0,0,0),self.local)
        self.assert_store(expected1,(1,0,0,0),self.api1)
        self.assert_store(expected1,(1,1,0,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_initial_setup(self):
        expectedL = [{'id':9, 'key':1, 'share':4, 'pull':10, 'push1':2, 'push2':None}]
        expected1 = [{'key':1, 'share':4, 'pull':10, 'push1':2}]
        self.api1.ddata = expected1
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expectedL,(1,1,0,0),self.local)
        self.assert_store(expected1,(1,0,0,0),self.api1)
        self.assert_store(expected1,(1,1,0,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)

    def test_one_arm_mixed_update(self):
        self.local.ddata = [{'id':5, 'key':1, 'share':7, 'pull':6, 'push1':2, 'push2':None}]
        self.snapshot1.ddata = [{'key':1, 'share':4, 'pull':3, 'push1':2}]
        self.api1.ddata = [{'key':1, 'share':8, 'pull':3, 'push1':5}]
        expectedL = [{'id':5, 'key':1, 'share':7, 'pull':6, 'push1':5, 'push2':None}]
        expected1 = [{'key':1, 'share':7, 'pull':6, 'push1':5}]
        cynq = Controller(self.arm1).cynq()
        self.assert_store(expectedL,(1,0,1,0),self.local)
        self.assert_store(expected1,(1,0,1,0),self.api1)
        self.assert_store(expected1,(1,0,1,0),self.snapshot1)
        self.assert_no_changes_on_another_cynq(cynq)


    def test_one_arm_pushkey_local_create(self):
        class PushKeySpec(BaseSpec):
            name = 'pushkey'
            rpushed = ('key',)
            rpulled = ('pull',)
            shared = ('share',)
            key = 'key'

        spec = PushKeySpec()
        local = VoodooStore(attrs=['key','pull','share','id'], key='id', push_attrs=['pull'], keygen=lambda dobj: 9, pushgen=lambda dobj: 10)
        api = VoodooStore(spec=spec, keygen=lambda dobj: 11)
        snapshot = VoodooStore(spec=spec)
        arm = Arm(spec, api, local, snapshot)
        local.ddata = [{'id':8, 'share':4, 'pull':3}]
        expectedL = [{'id':8, 'pull':3, 'share':4, 'key':11}]
        expectedR = [{'key':11, 'pull':3, 'share':4}]
        cynq = Controller(arm).cynq()
        self.assert_store(expectedL,(1,0,1,0),local)
        self.assert_store(expectedR,(1,1,0,0),api)
        self.assert_store(expectedR,(1,1,0,0),snapshot)
        self.assert_no_changes_on_another_cynq(cynq, local)

    def test_two_arm_large_cynq(self):
        self.local.generate_seeds(1000)
        self.api1.generate_seeds(1000)
        self.api2.generate_seeds(1000)
        cynq = Controller(self.arm1,self.arm2).cynq()
        self.log.debug("local changes: %s", self.local.post_stats)
        self.log.debug("api1 changes: %s", self.api1.post_stats)
        self.log.debug("api2 changes: %s", self.api2.post_stats)
        self.log.debug("snapshot1 changes: %s", self.snapshot1.post_stats)
        self.log.debug("snapshot2 changes: %s", self.snapshot2.post_stats)
        self.assert_no_changes_on_another_cynq(cynq)


    def assert_no_changes_on_another_cynq(self, controller, local=None):
        if not local: local = self.local
        local._clear_cache(); local._clear_stats()
        for arm in controller.arms:
            for s in arm.stores:
                s._clear_cache();
                if s != arm.local: s._clear_stats()

        # make sure it's all equal to start
        arm_ddata = {}
        for arm in controller.arms:
            self.assert_equal_dlists(arm.api.attrs, arm.api.ddata, local.ddata)
            self.assert_equal_dlists(arm.api.attrs, arm.api.ddata, arm.snapshot.ddata)
            self.assert_equal_dlists(arm.api.attrs, local.ddata, arm.snapshot.ddata)  # overkill just in case
            arm_ddata[arm] = arm.api.ddata
        local_ddata = local.ddata

        controller.cynq()

        for arm in controller.arms:
            self.assert_store(local_ddata,(1,0,0,0),local)
            self.assert_store(arm_ddata[arm],(1,0,0,0),arm.api)
            self.assert_store(arm_ddata[arm],(1,0,0,0),arm.snapshot)


    def assert_store(self, *args):
        args = list(args)
        if len(args)==3: args[2:2]=[args[1]]  # if no post/pre disctinction, then just double up
        expected_ddata, expected_pre_stats, expected_post_stats, store = args
        self.assertEqual(expected_pre_stats, store.pre_stats)
        self.assertEqual(expected_post_stats, store.post_stats)
        self.assert_equal_dlists(store.attrs, expected_ddata, store.ddata)

