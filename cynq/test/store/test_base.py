import unittest2
from cynq.voodoo import VoodooMemoryApi, VoodooRemoteSpec, VoodooLocalSpec
from copy import deepcopy
from cynq.store import BaseStore
from uuid import uuid4
#from pprint import pprint

class TestSharedKeyVoodooRemoteSpec(VoodooRemoteSpec):
    name = 'remote'
    pushed = ('push',)
    pulled = ('pull',)
    shared = ('share','key')
    key = 'key'

class TestPushedKeyVoodooRemoteSpec(VoodooRemoteSpec):
    name = 'remote'
    pushed = ('push','key',)
    pulled = ('pull',)
    shared = ('share',)
    key = 'key'

class TestVoodooLocalSpec(VoodooLocalSpec):
    extras = ('id',)
    key = 'id'


class TestCase(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read(self):
        spec = TestSharedKeyVoodooRemoteSpec(VoodooMemoryApi())
        expected = deepcopy(spec.api.seed(4))
        store = BaseStore(spec)
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, store.list_)
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)

    def test_read_caching(self):
        spec = TestSharedKeyVoodooRemoteSpec(VoodooMemoryApi())
        expected = deepcopy(spec.api.seed(4))
        store = BaseStore(spec)
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, store.list_)
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, store.list_)
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)

    def test_read_failure(self):
        spec = TestSharedKeyVoodooRemoteSpec(VoodooMemoryApi(pre_fail_lambda=lambda obj,op,tries: op=='read' and tries<=1 ))
        expected = deepcopy(spec.api.seed(4))
        store = BaseStore(spec)
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        with self.assertRaises(StandardError): store.list_
        self.assertEquals({'pre':(1,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, store.list_)
        self.assertEquals({'pre':(2,0,0,0),'post':(1,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, store.list_)
        self.assertEquals({'pre':(2,0,0,0),'post':(1,0,0,0)},spec.api.stats)

    def test_create_caching(self):
        spec = TestPushedKeyVoodooRemoteSpec(VoodooMemoryApi())
        seeds = deepcopy(spec.api.seed(3))
        store = BaseStore(spec)
        store.get_hash('key')  # ensure this is built up
        obj = spec.api.build_seed()
        expected_obj = deepcopy(obj)
        expected_list = seeds + [expected_obj]

        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)
        store.create(obj)
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)

        self.assert_equal_object_lists(expected_list, store.list_)
        self.assertEquals(id(obj), id(store.list_[-1]))
        for o in expected_list:
            self.assertEquals(o, store.get_hash('key')[o['key']])

        store.persist_changes()
        self.assertEquals({'pre':(1,1,0,0),'post':(1,1,0,0)},spec.api.stats)
        self.assert_not_equal_object_lists(expected_list, store.list_)
        self.assert_equal_object_lists(expected_list, store.list_, remove_attrs=['key', 'push'])
        self.assertEquals(id(obj), id(store.list_[-1]))
        self.assertNotIn(expected_obj['key'], store.get_hash('key'))
        for o in store.list_:
            self.assertEquals(o, store.get_hash('key')[o['key']])

    def test_update_caching(self):
        spec = TestSharedKeyVoodooRemoteSpec(VoodooMemoryApi())
        spec.api.seed(3)
        store = BaseStore(spec)
        store.get_hash('key')  # ensure this is built up
        obj = store.list_[0]
        obj['share'] = str(uuid4())[:4]
        expected_obj = deepcopy(obj)
        expected_list = [deepcopy(obj)] + deepcopy(store.list_[1:])

        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)
        store.update(obj)
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)

        self.assert_equal_object_lists(expected_list, store.list_)
        self.assertEquals(id(obj), id(store.list_[0]))
        for o in expected_list:
            self.assertEquals(o, store.get_hash('key')[o['key']])

        store.persist_changes()
        self.assertEquals({'pre':(1,0,1,0),'post':(1,0,1,0)},spec.api.stats)
        self.assert_not_equal_object_lists(expected_list, store.list_)
        self.assert_equal_object_lists(expected_list, store.list_, remove_attrs=['key', 'push'])
        self.assertEquals(id(obj), id(store.list_[0]))
        for o in store.list_:
            self.assertEquals(o, store.get_hash('key')[o['key']])

    def test_delete_caching(self):
        spec = TestVoodooRemoteSpec(VoodooMemoryApi())
        seeds = deepcopy(spec.api.seed(3))
        store = BaseStore(spec)
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        expected_obj = deepcopy(seeds[-1])
        expected_list = seeds[0:-2]
        store.delete(obj)
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)
        print store.list_
        self.assert_equal_object_lists(expected_list, store.list_)
        self.assertEquals(id(obj), id(store.list_[-1]))

        store.persist_changes()
        self.assertEquals({'pre':(1,1,0,0),'post':(1,1,0,0)},spec.api.stats)
        self.assert_not_equal_object_lists(expected_list, store.list_)
        self.assert_equal_object_lists(expected_list, store.list_, remove_attrs=['push'])
        self.assertEquals(id(obj), id(store.list_[-1]))

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


