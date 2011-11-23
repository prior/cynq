import unittest2
from cynq.spec import RemoteSpec, LocalSpec, TestMemorySpec
from cynq.phase import RemoteCreate
from junction import Junction

class TestRemoteSpec(RemoteSpec, TestMemorySpec):
    def __init__(self, seeds=None):
        super(TestRemoteSpec,self).__init__(seeds)
    id_ = 'test_remote'
    pushed = ['two']
    pulled = ['one']
    shared = ['key','share']
    key = 'key'

class TestLocalSpec(LocalSpec, TestMemorySpec):
    def __init__(self, seeds=None):
        super(TestLocalSpec,self).__init__(seeds)

class TestCase(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_normal_remote_create(self):
        rs = TestRemoteSpec([{'key':1, 'one':1, 'two':1, 'share':1}], push_gen=(lambda attr: 'out'))
        ls = TestLocalSpec([{'key':2, 'one':2, 'two':2, 'share':2}])
        self.assertEquals((0,0,0,0),rs.crud_stats)
        self.assertEquals((0,0,0,0),ls.crud_stats)
        RemoteCreate(Junction(ls,rs)).execute()
        self.assertEquals((1,1,0,0),rs.crud_stats)
        self.assertEquals((1,0,0,0),ls.crud_stats)
        self.assertEquals([{'key':2, 'one':2, 'shared':2}], rs.creates_before)
        self.assertEquals([{'key':2, 'one':2, 'shared':2, 'two': 'out'}], rs.creates_after)
        
#NOTE: gotta make the final update pull back remote_expectations!


