import unittest2
from cynq.voodoo import VoodooMemoryApi, VoodooRemoteSpec
from copy import deepcopy
import uuid


class TestVoodooRemoteSpec(VoodooRemoteSpec):
    id_ = 'test'
    pushed = ['push']
    pulled = ['pull']
    shared = ['key','share']
    key = 'key'

class TestCase(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_accounting(self):
        seeds = self.build_seeds(TestVoodooRemoteSpec,4)
        api = VoodooMemoryApi(seeds = deepcopy(seeds))
        spec = TestVoodooRemoteSpec(api)
        self.assertEquals({'pre':(0,0,0,0),'post':(0,0,0,0)},api.stats)
        self.assertEquals(deepcopy(seeds), spec.all_())
        self.assertEquals({'pre':(1,0,0,0),'post':(1,0,0,0)},api.stats)
        self.assertEquals(deepcopy(seeds), spec.all_())
        self.assertEquals({'pre':(2,0,0,0),'post':(2,0,0,0)},api.stats)

    def _build_seeds(self, spec_kls, count):
        return (self._build_seed(spec_kls) for i in xrange(count))

    def _build_seed(self, spec_kls):
        dict((attr,str(uuid.uuid4())) for attr in (spec_kls.pushed + spec_kls.pulled + spec_kls.shared))


