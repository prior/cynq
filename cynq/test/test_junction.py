import unittest2
from cynq.master import Cynq
from cynq.voodoo import VoodooMemoryApi, VoodooRemoteSpec, VoodooLocalSpec
from copy import deepcopy
import logger; logger.setup()


LOCAL_ALIVE_SYNCED_EXPECTED = {'deleted_at':None, 'synced_at':3, 'syncable_updated_at':3,'remote_expected':True}
LOCAL_DEAD_SYNCED_EXPECTED = {'deleted_at':1, 'synced_at':3, 'syncable_updated_at':3,'remote_expected':True}
LOCAL_ALIVE_SYNCED_UNEXPECTED = {'deleted_at':None, 'synced_at':3, 'syncable_updated_at':3,'remote_expected':False}
LOCAL_DEAD_SYNCED_UNEXPECTED = {'deleted_at':1, 'synced_at':3, 'syncable_updated_at':3,'remote_expected':False}
LOCAL_ALIVE_SYNCED = {'deleted_at':None, 'synced_at':3, 'syncable_updated_at':3,'remote_expected':None}
LOCAL_DEAD_SYNCED = {'deleted_at':1, 'synced_at':3, 'syncable_updated_at':3,'remote_expected':None}
LOCAL_ALIVE_SYNCEDNOW_EXPECTED = {'deleted_at':None, 'synced_at':'NOW', 'syncable_updated_at':'NOW','remote_expected':True}

class TestCase(unittest2.TestCase):
    def setUp(self): print
    def tearDown(self): pass

    def test_nochange(self):
        class RS(VoodooRemoteSpec): 
            name='remote'
            pushed=('push',); pulled=('pull',); shared=('key',); key='key'
            seeds = [{'key':2, 'push':3, 'pull':4}]

        class LS(VoodooLocalSpec): 
            pushed = ('id','key',)
            key='id'
            seeds = [ dict(LOCAL_ALIVE_SYNCED_EXPECTED, **{'id':1, 'key':2, 'push':3, 'pull':4}) ]

        expected_remote = [ {'key':2, 'push':3, 'pull':4} ]
        expected_local = [ dict(LOCAL_ALIVE_SYNCED_EXPECTED, **{'id':1, 'key':2, 'push':3, 'pull':4}) ]
        expected_changes = ((0,0,0,0,0,0),(0,0,0,0,0,0))
        self._assert_proper_cynq((expected_local, (expected_remote,)), expected_changes, (LS([RS]),(RS(),)))

    def test_remote_create_pulled_key(self):
        class RS(VoodooRemoteSpec): 
            name='remote'
            pulled=('key',); shared=('share',); key='key'
            seeds = []

        class LS(VoodooLocalSpec): 
            pushed = ('id','key',)
            key='id'
            seeds = [ dict(LOCAL_ALIVE_SYNCED_UNEXPECTED, **{'id':1, 'key':2, 'share':3}) ]

        expected_remote = [ {'key':2, 'share':3} ]
        expected_local = [ dict(LOCAL_ALIVE_SYNCEDNOW_EXPECTED, **{'id':1, 'key':2, 'share':3}) ]
        expected_changes = ((0,0,1,0,0,0),(1,0,0,0,0,0))
        self._assert_proper_cynq((expected_local, (expected_remote,)), expected_changes, (LS([RS]),(RS(),)))

    def test_remote_create_pulled_key_with_pushing(self):
        class RS(VoodooRemoteSpec): 
            name='remote'
            pushed=('push',); pulled=('key',); shared=('share',); key='key'
            seeds = []
            push_lambda = staticmethod(lambda obj,attr,op: obj.get(attr) or 5)

        class LS(VoodooLocalSpec): 
            pushed = ('id','key',)
            key='id'
            seeds = [ dict(LOCAL_ALIVE_SYNCED_UNEXPECTED, **{'id':1, 'key':2, 'push':4, 'share':3}) ]

        expected_remote = [ {'key':2, 'push':5, 'share':3} ]
        expected_local = [ dict(LOCAL_ALIVE_SYNCEDNOW_EXPECTED, **{'id':1, 'key':2, 'push':5, 'share':3}) ]
        expected_changes = ((0,0,1,0,0,0),(1,0,0,0,0,0))
        self._assert_proper_cynq((expected_local, (expected_remote,)), expected_changes, (LS([RS]),(RS(),)))

    def test_remote_create_pushed_key(self):
        class RS(VoodooRemoteSpec): 
            name='remote'
            pushed=('key',); pulled=('pull',); shared=('share',); key='key'
            seeds = []
            push_lambda = staticmethod(lambda obj,attr,op: obj.get(attr) or 5)

        class LS(VoodooLocalSpec): 
            pushed = ('id','key',)
            key='id'
            seeds = [ dict(LOCAL_ALIVE_SYNCED_UNEXPECTED, **{'id':1, 'pull':2, 'share':3}) ]

        expected_remote = [ {'key':5, 'pull':2, 'share':3} ]
        expected_local = [ dict(LOCAL_ALIVE_SYNCEDNOW_EXPECTED, **{'id':1, 'key':5, 'share':3}) ]
        expected_changes = ((0,0,1,0,0,0),(1,0,0,0,0,0))
        self._assert_proper_cynq((expected_local, (expected_remote,)), expected_changes, (LS([RS]),(RS(),)))

    def test_remote_update_shared_key(self):
        class RS(VoodooRemoteSpec): 
            name='remote'
            pulled=('pull',); pushed=('push',); shared=('key',); key='key'
            seeds = [ {'key':2, 'push':3, 'pull':4} ]

        class LS(VoodooLocalSpec): 
            pushed = ('id',)
            key='id'
            seeds = [ dict(LOCAL_ALIVE_SYNCED_EXPECTED, **{'id':1, 'key':2, 'push':3, 'pull':5}) ]

        expected_remote = [ {'key':2, 'push':3, 'pull':5} ]
        expected_local = [ dict(LOCAL_ALIVE_SYNCEDNOW_EXPECTED, **{'id':1, 'key':2, 'push':3, 'pull':5}) ]
        expected_changes = ((0,0,0,0,0,0),(0,0,1,0,0,0))
        self._assert_proper_cynq((expected_local, (expected_remote,)), expected_changes, (LS([RS]),(RS(),)))

    def test_local_create_shared_key(self):
        class RS(VoodooRemoteSpec): 
            name='remote'
            pushed=('push',); shared=('key',); key='key'
            seeds = [ {'key':1, 'push':3} ]

        class LS(VoodooLocalSpec): 
            pushed = ('id',)
            key='id'
            seeds = []
            push_lambda = staticmethod(lambda obj,attr,op: attr=='id' and 4)

        expected_remote = [ {'key':1, 'push':3} ]
        expected_local = [ dict(LOCAL_ALIVE_SYNCEDNOW_EXPECTED, **{'id':4, 'key':1, 'push':3}) ]
        expected_changes = ((1,0,0,0,0,0),(0,0,0,0,0,0))
        self._assert_proper_cynq((expected_local, (expected_remote,)), expected_changes, (LS([RS]),(RS(),)))

    def test_local_create_shared_key_with_extra_pulling(self):
        class RS(VoodooRemoteSpec): 
            name='remote'
            pushed=('push',); pulled=('pull',); shared=('key',); key='key'
            seeds = [ {'key':1, 'pull':2, 'push':3} ]

        class LS(VoodooLocalSpec): 
            pushed = ('id','pull',)
            key='id'
            seeds = []
            push_lambda = staticmethod(lambda obj,attr,op: attr=='id' and 4 or attr=='pull' and 5)

        expected_remote = [ {'key':1, 'pull':2, 'push':3} ]
        expected_local = [ dict(LOCAL_ALIVE_SYNCEDNOW_EXPECTED, **{'id':4, 'key':1, 'pull':5, 'push':3}) ]
        expected_changes = ((1,0,0,0,0,0),(0,0,0,0,0,0))
        ls = LS([RS]); rs = RS()
        self._assert_proper_cynq((expected_local, (expected_remote,)), expected_changes, (ls,(rs,)), False)

        expected_remote = [ {'key':1, 'pull':5, 'push':3} ]
        expected_local = [ dict(LOCAL_ALIVE_SYNCEDNOW_EXPECTED, **{'id':4, 'key':1, 'pull':5, 'push':3}) ]
        expected_changes = ((0,0,0,0,0,0),(0,0,1,0,0,0))
        self._assert_proper_cynq((expected_local, (expected_remote,)), expected_changes, (ls,(rs,)))


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

    def _assert_no_changes_on_subsequent_cynqs(self, cq):
        remote_all_hash = dict((rs,deepcopy(rs.spec.all_())) for rs in cq.remote_stores)
        local_all = deepcopy(cq.local_store.spec.all_())
        cq.cynq()
        for remote_store in cq.remote_stores:
            self.assertEquals({'creates':{True:0,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}, remote_store._stats)
        self.assertEquals({'creates':{True:0,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}, cq.local_store._stats)
        for rs in remote_all_hash:
            self._assert_equal_object_lists(remote_all_hash[rs], rs.spec.all_())
        self._assert_equal_object_lists(local_all, cq.local_store.spec.all_())

    def _assert_proper_cynq(self, expected, changes, specs, subsequent_nochange=True):
        cq = Cynq(specs[0],specs[1])
        cq.cynq()
        started_at = cq.cynq_started_at

        self.assertEquals({True:changes[0][0],False:changes[0][1]}, cq.local_store._stats['creates'])
        self.assertEquals({True:changes[0][2],False:changes[0][3]}, cq.local_store._stats['updates'])
        self.assertEquals({True:changes[0][4],False:changes[0][5]}, cq.local_store._stats['deletes'])
            
        for i in xrange(len(cq.remote_stores)):
            self.assertEquals({True:changes[i+1][0],False:changes[i+1][1]}, cq.remote_stores[i]._stats['creates'])
            self.assertEquals({True:changes[i+1][2],False:changes[i+1][3]}, cq.remote_stores[i]._stats['updates'])
            self.assertEquals({True:changes[i+1][4],False:changes[i+1][5]}, cq.remote_stores[i]._stats['deletes'])

        local_expected = [dict((k,v=='NOW' and started_at or v) for k,v in o.iteritems()) for o in expected[0]]
        self._assert_equal_object_lists(local_expected, cq.local_store.spec.all_())
        for i in xrange(len(cq.remote_stores)):
            self._assert_equal_object_lists(expected[1][i], cq.remote_stores[i].spec.all_())

        if subsequent_nochange:
            self._assert_no_changes_on_subsequent_cynqs(cq)

    def _assert_equal_object_lists(self, list1, list2, remove_attrs=None):
        if remove_attrs:
            list1 = self._remove_attrs_in_list(deepcopy(list1), remove_attrs)
            list2 = self._remove_attrs_in_list(deepcopy(list2), remove_attrs)
        t1,t2 = self._to_tuples(list1,list2)
        self.assertEquals(t1,t2)

    def _assert_not_equal_object_lists(self, list1, list2):
        t1,t2 = self._to_tuples(list1,list2)
        self.assertNotEquals(t1,t2)

    def _remove_attrs_in_list(self, list_, attrs):
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


