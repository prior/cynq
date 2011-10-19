import unittest2
import uuid
from cynq.stores.read_cache import ReadCache
from cynq.stores.base import Base


class TestStore(Base):
    def __init__(self):
        super(TestStore,self).__init__()
        self.creates = []
        self.updates = []
        self.deletes = []
        self.lists = []

    def list_(self):
        self.lists.append(True)
        return self._list

    def create(self, obj):
        self.creates.append(obj)
        return obj

    def update(self, obj):
        self.updates.append(obj)
        return obj

    def delete(self, obj):
        self.deletes.append(obj)
        return obj

class TestObject(object):
    def __init__(self):
        self.attribute = str(uuid.uuid4())[:16]


LIST_SIZE = 4

class ReadCacheTest(unittest2.TestCase):

    def setUp(self):
        self.test_store = TestStore()
        self.test_cache = ReadCache(self.test_store)
        self.test_list = [TestObject() for i in xrange(0,LIST_SIZE)]
        self.test_store._list = self.test_list

    def tearDown(self):
        pass

    def test_list_cached(self):
        retlist1 = self.test_cache.list_()
        self.assertEquals(self.test_list, retlist1)

        new_test_list = self.test_list + [TestObject()]
        self.assertNotEquals(new_test_list, self.test_list)

        self.test_store._list = new_test_list
        retlist2 = self.test_cache.list_()
        self.assertNotEquals(new_test_list, retlist2)
        self.assertEquals(retlist1, retlist2)
        self.assertEquals(self.test_list, retlist1)
        self.assertEquals(1, len(self.test_store.lists))

    def test_create_adjustment(self):
        obj = TestObject()
        self.assertNotIn(obj,self.test_cache.list_())
        self.test_cache.create(obj)
        self.assertIn(obj,self.test_cache.list_())
        self.assertEquals([obj],self.test_store.creates)
        self.assertEquals(LIST_SIZE+1, len(self.test_cache.list_()))

    def test_update_adjustment(self):
        obj = self.test_list[LIST_SIZE/3]
        self.assertIn(obj,self.test_cache.list_())
        obj.attribute = str(uuid.uuid4())[:16]
        self.test_cache.update(obj)
        self.assertIn(obj,self.test_cache.list_())
        self.assertEquals([obj],self.test_store.updates)
        self.assertEquals(LIST_SIZE, len(self.test_cache.list_()))

    def test_delete_adjustment(self):
        obj = self.test_list[LIST_SIZE/2]
        self.assertIn(obj,self.test_cache.list_())
        self.test_cache.delete(obj)
        self.assertNotIn(obj,self.test_cache.list_())
        self.assertEquals([obj],self.test_store.deletes)
        self.assertEquals(LIST_SIZE-1, len(self.test_cache.list_()))



if __name__ == '__main__':
    unittest2.main()
