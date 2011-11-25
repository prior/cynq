import unittest2
from cynq.voodoo import VoodooMemoryApi, VoodooRemoteSpec, VoodooLocalSpec
from copy import deepcopy
import uuid
#from pprint import pprint

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

    def test_read_accounting(self):
        spec = TestVoodooRemoteSpec(VoodooMemoryApi())
        expected = deepcopy(spec.api.seed(4))
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, spec.all_())
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, spec.all_())
        self.assertEquals({'pre':(2,0,0,0),'post':(2,0,0,0)},spec.api.stats)

    def test_create_accounting(self):
        spec = TestVoodooRemoteSpec(VoodooMemoryApi())
        expected_list = deepcopy(spec.api.seed(3))
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        obj = spec.api.build_seed()
        expected_obj = deepcopy(obj)
        spec.single_create(obj)
        self.assertEquals({'pre':(0,1,0,0),'post':(0,1,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected_list + [obj], spec.all_())
        self.assertEquals(expected_obj, spec.api.pre_create[0])
        self.assertNotEquals(expected_obj, spec.api.post_create[0])
        del expected_obj['push']
        del spec.api.post_create[0]['push']
        self.assertEquals(expected_obj, spec.api.post_create[0])

    def test_update_accounting(self):
        spec = TestVoodooRemoteSpec(VoodooMemoryApi())
        expected_list = deepcopy(spec.api.seed(3))
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        obj = deepcopy(expected_list[0])
        obj['share'] = str(uuid.uuid4())[:4]
        expected_obj = deepcopy(obj)
        spec.single_update(obj)
        self.assertEquals({'pre':(0,0,1,0),'post':(0,0,1,0)},spec.api.stats)
        self.assert_not_equal_object_lists(expected_list, spec.all_())
        self.assert_equal_object_lists(expected_list, spec.all_(), remove_attrs=['share','push'])
        self.assertEquals(expected_obj, spec.api.pre_update[0])
        self.assertNotEquals(expected_obj, spec.api.post_update[0])
        del expected_obj['push']
        del spec.api.post_update[0]['push']
        self.assertEquals(expected_obj, spec.api.post_update[0])

    def test_delete_accounting(self):
        spec = TestVoodooRemoteSpec(VoodooMemoryApi())
        expected_list = deepcopy(spec.api.seed(3))
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        obj = deepcopy(expected_list[0])
        expected_obj = deepcopy(obj)
        spec.single_delete(obj)
        self.assertEquals({'pre':(0,0,0,1),'post':(0,0,0,1)},spec.api.stats)
        self.assert_equal_object_lists(deepcopy(expected_list[1:]), spec.all_())
        self.assertEquals(expected_obj, spec.api.pre_delete[0])
        self.assertEquals(expected_obj, spec.api.post_delete[0])

    def test_localish_api_hookup_on_read_accounting(self):
        spec = TestVoodooLocalSpec(VoodooMemoryApi(), [TestVoodooRemoteSpec])
        expected = deepcopy(spec.api.seed(3))
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, spec.all_())
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, spec.all_())
        self.assertEquals({'pre':(2,0,0,0),'post':(2,0,0,0)},spec.api.stats)

    def test_pre_failures(self):
        spec = TestVoodooRemoteSpec(VoodooMemoryApi(pre_fail_lambda = (lambda obj,op: op!='read')))
        seeded_list = deepcopy(spec.api.seed(4))
        self.assert_equal_object_lists(seeded_list, spec.all_())

        create_obj = deepcopy(spec.api.build_seed())
        self.assertRaises(StandardError, spec.single_create, *[create_obj])
        self.assertEquals({'pre':(1,1,0,0),'post':(1,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(seeded_list, spec.all_())

        update_obj = deepcopy(seeded_list[0])
        update_obj['share'] = str(uuid.uuid4())[:4]
        self.assertRaises(StandardError, spec.single_update, *[update_obj])
        self.assertEquals({'pre':(2,1,1,0),'post':(2,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(seeded_list, spec.all_())

        delete_obj = deepcopy(seeded_list[1])
        self.assertRaises(StandardError, spec.single_delete, *[delete_obj])
        self.assertEquals({'pre':(3,1,1,1),'post':(3,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(seeded_list, spec.all_())

    def test_post_failures(self):
        spec = TestVoodooRemoteSpec(VoodooMemoryApi(post_fail_lambda = (lambda obj,op: op!='read')))
        seeded_list = deepcopy(spec.api.seed(1))
        self.assert_equal_object_lists(seeded_list, spec.all_())

        create_obj = spec.api.build_seed()
        self.assertRaises(StandardError, spec.single_create, *[create_obj])
        new_list = deepcopy(seeded_list + [create_obj])
        self.assertEquals({'pre':(1,1,0,0),'post':(1,0,0,0)},spec.api.stats)
        self.assert_not_equal_object_lists(new_list, spec.all_())
        self.assert_equal_object_lists(new_list, spec.all_(), remove_attrs=['push'])
        seeded_list = spec.all_()

        update_obj = deepcopy(seeded_list[0])
        update_obj['share'] = str(uuid.uuid4())[:4]
        new_list = deepcopy([update_obj] + seeded_list[1:])
        self.assertRaises(StandardError, spec.single_update, *[update_obj])
        self.assertEquals({'pre':(4,1,1,0),'post':(4,0,0,0)},spec.api.stats)
        self.assert_not_equal_object_lists(new_list, spec.all_())
        self.assert_equal_object_lists(new_list, spec.all_(), remove_attrs=['push'])
        seeded_list = spec.all_()

        delete_obj = deepcopy(seeded_list[1])
        new_list = deepcopy(seeded_list[0:1] + seeded_list[2:])
        self.assertRaises(StandardError, spec.single_delete, *[delete_obj])
        self.assertEquals({'pre':(7,1,1,1),'post':(7,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(new_list, spec.all_())

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


