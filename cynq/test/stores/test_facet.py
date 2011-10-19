import unittest2
import uuid
from cynq.stores.facet import Facet
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

class FacetTest(unittest2.TestCase):

    def setUp(self):
        self.test_store = TestStore()
        self.test_cache = Facet(self.test_store, 'attribute')
        self.test_list = [TestObject() for i in xrange(0,LIST_SIZE)]
        self.test_store._list = self.test_list

        self.other_store = TestStore()
        self.other_cache = Facet(self.other_store, 'attribute')
        self.other_list = self.test_list[LIST_SIZE/2:LIST_SIZE/2+1]
        self.other_store._list = self.other_list

    def tearDown(self):
        pass

    def test_list_cached(self):
        retlist1 = self.test_cache.list_()
        self.assertEquals(set(self.test_list), set(retlist1))

        new_test_list = self.test_list + [TestObject()]
        self.assertNotEquals(new_test_list, self.test_list)

        self.test_store._list = new_test_list
        retlist2 = self.test_cache.list_()
        self.assertNotEquals(new_test_list, retlist2)
        self.assertEquals(retlist1, retlist2)
        self.assertEquals(set(self.test_list), set(retlist1))
        self.assertEquals(1, len(self.test_store.lists))

    def test_create_adjustment(self):
        obj = TestObject()
        self.assertIsNone(self.test_cache[obj.attribute])
        self.assertNotIn(obj,self.test_cache.list_())
        self.test_cache.create(obj)
        self.assertIn(obj,self.test_cache.list_())
        self.assertEquals([obj],self.test_store.creates)
        self.assertEquals(LIST_SIZE+1, len(self.test_cache.list_()))
        self.assertEquals(obj,self.test_cache[obj.attribute])

    def test_update_adjustment(self):
        obj = self.test_list[LIST_SIZE/3]
        self.assertEquals(obj,self.test_cache[obj.attribute])
        self.assertIn(obj,self.test_cache.list_())
        self.test_cache.update(obj)
        self.assertIn(obj,self.test_cache.list_())
        self.assertEquals([obj],self.test_store.updates)
        self.assertEquals(LIST_SIZE, len(self.test_cache.list_()))
        self.assertEquals(obj,self.test_cache[obj.attribute])

    def test_delete_adjustment(self):
        obj = self.test_list[LIST_SIZE/2]
        self.assertIn(obj,self.test_cache.list_())
        self.test_cache.delete(obj)
        self.assertNotIn(obj,self.test_cache.list_())
        self.assertEquals([obj],self.test_store.deletes)
        self.assertEquals(LIST_SIZE-1, len(self.test_cache.list_()))
        self.assertIsNone(self.test_cache[obj.attribute])

    def test_iterator(self):
        self.assertEquals(set([o.attribute for o in self.test_list]),set(list(self.test_cache)))

    def test_subtraction(self):
        obj = self.other_list[0]
        expected_set = set([o.attribute for o in self.test_list if o!=obj])
        self.assertEquals(expected_set, set(self.test_cache - self.other_cache))
        expected_set = set()
        self.assertEquals(expected_set, set(self.other_cache - self.test_cache))

    def test_intersection(self):
        obj = self.other_list[0]
        expected_set = set([obj.attribute])
        self.assertEquals(expected_set, set(self.test_cache & self.other_cache))
        self.assertEquals(expected_set, set(self.other_cache & self.test_cache))





if __name__ == '__main__':
    unittest2.main()
