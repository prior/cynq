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
        self.assertEquals(len(expected_list), len(spec.all_()))
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
        print expected
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, spec.all_())
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},spec.api.stats)
        self.assert_equal_object_lists(expected, spec.all_())
        self.assertEquals({'pre':(2,0,0,0),'post':(2,0,0,0)},spec.api.stats)

    def test_pre_failures(self):
        seeds = self._build_seeds(TestVoodooRemoteSpec,4)
        api = VoodooMemoryApi(seeds = deepcopy(seeds))
        spec = TestVoodooRemoteSpec(api)
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},api.stats)




    def _build_seeds(self, attrs, count):
        return [self._build_seed(attrs) for i in xrange(count)]

    def _build_seed(self, attrs):
        return dict((attr,str(uuid.uuid4())[:4]) for attr in attrs)

    def assert_equal_object_lists(self, list1, list2):
        tuple1 = tuple(sorted(tuple(sorted(o.iteritems())) for o in list1))
        tuple2 = tuple(sorted(tuple(sorted(o.iteritems())) for o in list2))
        self.assertEquals(tuple1,tuple2)


