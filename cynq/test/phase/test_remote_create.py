import unittest2
from cynq.spec import RemoteSpec, LocalSpec, TestMemorySpec
from cynq.phase import RemoteCreate
from junction import Junction

class TestRemoteSpec(RemoteSpec, TestMemorySpec):
    def __init__(self, seeds=None, push_gen=None):
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

    def test_proper_seeds(self): #_TODO: move
        seed = [{'key':4}, {'one':9}]
        local_seed = [{'key':2, 'one':2, 'two':2, 'share':2}]
        expected_creates_before = [{

        self.assertRemoteCreate(self, 1)

        rs = TestRemoteSpec(copy(remote_seed), push_gen=(lambda attr: 'out'))
        ls = TestLocalSpec(copy(local_seed))
        jn = Junction(ls,rs)
        self.assertEquals(remote_seed, rs.list_)
        self.assertEquals(local_seed, ls.list_)
        self.assertEquals((0,0,0,0),rs.crud_stats)
        self.assertEquals((0,0,0,0),ls.crud_stats)
        self.

    def test_normal_remote_create(self):
        remote_seed = [{'key':1, 'one':1, 'two':1, 'share':1}]
        local_seed = [{'key':2, 'one':2, 'two':2, 'share':2}]
        expected_creates_before = [{

        self.assertRemoteCreate(self, 1)

        rs = TestRemoteSpec(copy(remote_seed), push_gen=(lambda attr: 'out'))
        ls = TestLocalSpec(copy(local_seed))
        jn = Junction(ls,rs)
        self.assertEquals(remote_seed, rs.list_)
        self.assertEquals(local_seed, ls.list_)
        self.assertEquals((0,0,0,0),rs.crud_stats)
        self.assertEquals((0,0,0,0),ls.crud_stats)
        RemoteCreate(jn).execute()
        self.assertEquals((1,1,0,0),rs.crud_stats)
        self.assertEquals((1,0,0,0),ls.crud_stats)
        self.assertEquals([{'key':2, 'one':2, 'shared':2}], rs.creates_before)
        self.assertEquals([{'key':2, 'one':2, 'shared':2, 'two': 'out'}], rs.creates_after)
        self.assertEquals([
        

    def assert_remote_create(self, count):
        self.assertEquals((0,0,0,0),rs.crud_stats)
        self.assertEquals((0,0,0,0),ls.crud_stats)
        RemoteCreate(jn).execute()
        self.assertEquals((1,1,0,0),rs.crud_stats)
        self.assertEquals((1,0,0,0),ls.crud_stats)

#NOTE: gotta make the final update pull back remote_expectations!


