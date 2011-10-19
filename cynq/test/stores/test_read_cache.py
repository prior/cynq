import unittest2
from cynq.stores.read_cache import ReadCache
from cynq.test import helper


class TestObject(helper.TestObject):
    prepopulate_attributes = True
    attrs = ['attribute']

SIZE = 4
LIST = [TestObject() for i in xrange(0,SIZE)]


class ReadCacheTest(helper.TestCase):

    def setUp(self):
        self.store = helper.TestStore()
        self.cache = ReadCache(self.store)
        self.store._all = set(LIST)

    def tearDown(self):
        pass

    def test_list_cached(self):
        self.assertEquals(set(LIST), self.cache.all_())
        new_all = set(LIST+[TestObject()])
        self.store._all = new_all
        self.assertEquals(set(LIST), self.cache.all_())
        self.assertNotEquals(new_all, self.cache.all_())
        self.assert_store_changes(self.store, all_calls=1)

    def test_create_adjustment(self):
        obj = TestObject()
        self.assertNotIn(obj,self.cache.all_())
        self.cache.create(obj)
        self.assertIn(obj,self.cache.all_())
        self.assertEquals(SIZE+1, len(self.cache.all_()))
        self.assert_store_changes(self.store, creates=[obj])

    def test_update_adjustment(self):
        obj = LIST[SIZE/2]
        self.assertIn(obj,self.cache.all_())
        obj.change('attribute')
        self.cache.update(obj)
        self.assertIn(obj,self.cache.all_())
        self.assertEquals(SIZE, len(self.cache.all_()))
        self.assert_store_changes(self.store, updates=[obj])

    def test_delete_adjustment(self):
        obj = LIST[SIZE/2]
        self.assertIn(obj,self.cache.all_())
        self.cache.delete(obj)
        self.assertNotIn(obj,self.cache.all_())
        self.assertEquals(SIZE-1, len(self.cache.all_()))
        self.assert_store_changes(self.store, deletes=[obj])


if __name__ == '__main__':
    unittest2.main()
