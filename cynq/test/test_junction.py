import unittest2
from cynq.master import Cynq
from cynq.voodoo import VoodooMemoryApi, VoodooRemoteSpec, VoodooLocalSpec
from copy import deepcopy


class TestSharedKeyVoodooRemoteSpec(VoodooRemoteSpec):
    name = 'remote'
    pushed = ('push',)
    pulled = ('pull',)
    shared = ('key',)
    key = 'key'

class TestPushedKeyVoodooRemoteSpec(VoodooRemoteSpec):
    name = 'remote'
    pushed = ('key',)
    pulled = ('pull',)
    shared = ('share',)
    key = 'key'

class TestPulledKeyVoodooRemoteSpec(VoodooRemoteSpec):
    name = 'remote'
    pushed = ('push',)
    pulled = ('key',)
    shared = ('share',)
    key = 'key'

class TestVoodooLocalSpec(VoodooLocalSpec):
    extras = ('id','pull')
    key = 'id'


class TestCase(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assert_no_changes_on_subsequent_cynqs(self, cq):
        remote_all_hash = dict((rs,deepcopy(rs.spec.all_())) for rs in cq.remote_stores)
        local_all = deepcopy(cq.local_store.spec.all_())
        for remote_store in cq.remote_stores:
            remote_store.clear_stats()
        cq.local_store.clear_stats()
        cq.cynq()
        for remote_store in cq.remote_stores:
            self.assertEquals({'creates':{True:0,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}, remote_store._stats)
        self.assertEquals({'creates':{True:0,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}, cq.local_store._stats)
        for rs in remote_all_hash:
            self.assert_equal_object_lists(remote_all_hash[rs], rs.spec.all_())
        self.assert_equal_object_lists(local_all, cq.local_store.spec.all_())


    def test_basic_remote_create_pulled_key(self):
        remote_seeds = []
        local_seeds = [{'key':1, 'share':4, 'id':9, 'deleted_at':None, 'synced_at':None, 'sycnable_updated_at':None,'remote_expected':None}]
        rs = TestPulledKeyVoodooRemoteSpec(VoodooMemoryApi(seeds=remote_seeds, push_lambda=lambda obj,attr,op: 5 ))
        ls = TestVoodooLocalSpec(VoodooMemoryApi(seeds=local_seeds), [TestPulledKeyVoodooRemoteSpec])
        cq = Cynq(ls, [rs])
        cq.cynq()
        started_at = cq.cynq_started_at

        self.assertEquals({'creates':{True:1,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}, cq.remote_stores[0]._stats)
        self.assertEquals({'creates':{True:0,False:0}, 'updates':{True:1,False:0}, 'deletes':{True:0,False:0}}, cq.local_store._stats)

        self.assertEquals([{'key':1, 'push':5, 'share':4}], rs.all_())
        self.assertEquals([{'key':1, 'push':5, 'share':4, 'remote_expected':True, 'id':9, 'syncable_updated_at':started_at, 'synced_at':started_at, 'deleted_at':None}], ls.all_())

        self.assert_no_changes_on_subsequent_cynqs(cq)
        

    def test_basic_remote_create_pushed_key(self):
        remote_seeds = []
        local_seeds = [{'pull':3, 'share':4, 'id':9, 'deleted_at':None, 'synced_at':None, 'sycnable_updated_at':None,'remote_expected':None}]
        rs = TestPushedKeyVoodooRemoteSpec(VoodooMemoryApi(seeds=remote_seeds, push_lambda=lambda obj,attr,op: 5 ))
        ls = TestVoodooLocalSpec(VoodooMemoryApi(seeds=local_seeds), [TestPushedKeyVoodooRemoteSpec])
        cq = Cynq(ls, [rs])
        cq.cynq()
        started_at = cq.cynq_started_at

#        self.assert_changes((('remote',1,0,0,0,0,0),(0,0,1,0,0,0)), cq)

        self.assertEquals({'creates':{True:1,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}, cq.remote_stores[0]._stats)
        self.assertEquals({'creates':{True:0,False:0}, 'updates':{True:1,False:0}, 'deletes':{True:0,False:0}}, cq.local_store._stats)

        self.assert_equal_object_lists([{'key':5, 'pull':3, 'share':4}], rs.all_())
        self.assert_equal_object_lists([{'key':5, 'pull':3, 'share':4, 'remote_expected':True, 'id':9, 'syncable_updated_at':started_at, 'synced_at':started_at, 'deleted_at':None}], ls.all_())

        self.assert_no_changes_on_subsequent_cynqs(cq)

    def test_basic_local_create(self):
        remote_seeds = [{'share':4, 'key':5}]
        local_seeds = []
        rs = TestPushedKeyVoodooRemoteSpec(VoodooMemoryApi(seeds=remote_seeds, push_lambda=lambda obj,attr,op: 5 ))
        ls = TestVoodooLocalSpec(VoodooMemoryApi(seeds=local_seeds, push_lambda=lambda obj,attr,op: attr=='id' and 9 or attr=='pull' and 3), [TestPushedKeyVoodooRemoteSpec])
        cq = Cynq(ls, [rs])
        cq.cynq()
        started_at = cq.cynq_started_at

        self.assertEquals({'creates':{True:0,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}, cq.remote_stores[0]._stats)
        self.assertEquals({'creates':{True:1,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}, cq.local_store._stats)

        self.assert_equal_object_lists([{'key':5, 'pull':3, 'share':4}], rs.all_())
        self.assert_equal_object_lists([{'key':5, 'pull':3, 'share':4, 'remote_expected':True, 'id':9, 'syncable_updated_at':started_at, 'synced_at':started_at, 'deleted_at':None}], ls.all_())

    def test_large_sync(self):
        pass
        
    #def test_basic_filled_remote_create(self):
        #remote_seeds = [{'key':3, 'pull':2, 'share': ]
        #local_seeds = [{'key':1, 'pull':3, 'share':4, 'id':9}]
        #rs = TestVoodooRemoteSpec(VoodooMemoryApi(seeds=remote_seeds, push_lambda=lambda obj,attr,op: 5 ))
        #ls = TestVoodooLocalSpec(VoodooMemoryApi(seeds=local_seeds), [TestVoodooRemoteSpec])
        #cq = Cynq(ls, [rs], phases=['remote_create', 'final_phase'])
        #cq.cynq()
        #started_at = cq.cynq_started_at

        #self.assertEquals({'creates':{True:1,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}, cq.remote_stores[0]._stats)
        #self.assertEquals({'creates':{True:0,False:0}, 'updates':{True:1,False:0}, 'deletes':{True:0,False:0}}, cq.local_store._stats)

        #self.assertEquals([{'key':1, 'push':5, 'pull':3, 'share':4}], rs.all_())
        #self.assertEquals([{'key':1, 'push':5, 'pull':3, 'share':4, 'remote_expected':True, 'id':9, 'syncable_updated_at':started_at, 'synced_at':started_at, 'deleted_at':None}], ls.all_())


    def test_pushed_key_remote_create(self):
        pass

    def test_normal_remote_create(self):
        pass

    #def assert_remote_create(self, count):
        #self.assertEquals((0,0,0,0),rs.crud_stats)
        #self.assertEquals((0,0,0,0),ls.crud_stats)
        #RemoteCreate(jn).execute()
        #self.assertEquals((1,1,0,0),rs.crud_stats)
        #self.assertEquals((1,0,0,0),ls.crud_stats)

    def assert_equal_object_lists(self, list1, list2, remove_attrs=None):
        if remove_attrs:
            list1 = self.remove_attrs_in_list(deepcopy(list1), remove_attrs)
            list2 = self.remove_attrs_in_list(deepcopy(list2), remove_attrs)
        t1,t2 = self._to_tuples(list1,list2)
        self.assertEquals(t1,t2)

    def assert_not_equal_object_lists(self, list1, list2):
        t1,t2 = self._to_tuples(list1,list2)
        self.assertNotEquals(t1,t2)

    def remove_attrs_in_list(self, list_, attrs):
        for o in list_:
            for a in attrs:
                if o.has_key(a): 
                    del o[a]
        return list_
        
    def _to_tuples(self, l1, l2):
        t1 = tuple(sorted(tuple(sorted(o.iteritems())) for o in l1))
        t2 = tuple(sorted(tuple(sorted(o.iteritems())) for o in l2))
        return (t1,t2)


#NOTE: gotta make the final update pull back remote_expectations!


