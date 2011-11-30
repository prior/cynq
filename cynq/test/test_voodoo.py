import unittest2
from cynq.store import VoodooMemoryStore
from copy import deepcopy
import uuid
import helper
from cynq.arm import Arm
#from pprint import pprint

class TestVoodooArm(Arm):
    pushed = ('push',)
    pulled = ('pull',)
    shared = ('key','share')
    key = 'key'


class TestCase(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_accounting(self):
        store = VoodooMemoryStore()
        TestVoodooArm(store,store,store)
        expected = deepcopy(store.api.seed(4))
        self.assertEquals(((0,0,0,0),(0,0,0,0)),store.stats)
        helper.assert_equal_object_lists(expected, store._obj_list_convert(store.all_()))
        self.assertEquals(((1,0,0,0),(1,0,0,0)),store.stats)
        helper.assert_equal_object_lists(expected, store._obj_list_convert(store.all_()))
        self.assertEquals(((2,0,0,0),(2,0,0,0)),store.stats)

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

