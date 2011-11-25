import unittest2
from sanetime import sanetime
from cynq.voodoo import VoodooMemoryApi, VoodooRemoteSpec, VoodooLocalSpec
from cynq.phase import RemoteCreate
from cynq.store import LocalStore, RemoteStore
from cynq.junction import Junction
from copy import deepcopy


class TestVoodooRemoteSpec(VoodooRemoteSpec):
    name = 'remote'
    pushed = ('push',)
    pulled = ('pull',)
    shared = ('key','share')
    key = 'key'

class TestVoodooLocalSpec(VoodooLocalSpec):
    extras = ('id',)
    key = 'id'


class TestCase(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_hashing(self):



    def test_normal_remote_create(self):
        remote_seeds = []
        local_seeds = [{'key':1, 'push':2, 'pull':3, 'share':4}]

        remote_spec = TestVoodooRemoteSpec(VoodooMemoryApi(seeds=deepcopy(remote_seeds)))
        local_spec = TestVoodooLocalSpec(VoodooMemoryApi(seeds=deepcopy(local_seeds)), [TestVoodooRemoteSpec])

        jn = Junction(LocalStore(local_spec), RemoteStore(remote_spec))

        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},remote_spec.api.stats)
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},local_spec.api.stats)

        self.assertEquals(remote_seeds, jn.rs.list_)
        self.assertEquals(local_seeds, jn.ls.list_)

        rc = RemoteCreate(jn)
        rc.execute(sanetime())

        self.assertEquals({'pre':(1,1,0,0),'post':(1,1,0,0)},remote_spec.api.stats)
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},local_spec.api.stats)

        self.assertEquals([{'key':1, 'push':2, 'pull':5, 'share':4}], deepcopy(jn.rs.list_))
        self.assertEquals([{'key':1, 'push':2, 'pull':5, 'share':4}], deepcopy(jn.ls.list_))
        

    #def assert_remote_create(self, count):
        #self.assertEquals((0,0,0,0),rs.crud_stats)
        #self.assertEquals((0,0,0,0),ls.crud_stats)
        #RemoteCreate(jn).execute()
        #self.assertEquals((1,1,0,0),rs.crud_stats)
        #self.assertEquals((1,0,0,0),ls.crud_stats)

#NOTE: gotta make the final update pull back remote_expectations!


