import unittest2
from cynq.stores.facet import Facet
from cynq.test import helper


class TestObject(helper.TestObject):
    prepopulate_attributes = True
    attrs = ['attribute']

SIZE = 4
LIST = [TestObject() for i in xrange(0,SIZE)]


class FacetTest(helper.TestCase):

    def setUp(self):
        self.store = helper.TestStore()
        self.cache = Facet(self.store, 'attribute')
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
        self.assertEquals(obj,self.cache[obj.attribute])

    def test_update_adjustment(self):
        obj = LIST[SIZE/2]
        self.assertIn(obj,self.cache.all_())
        obj.change('attribute')
        self.cache.update(obj)
        self.assertIn(obj,self.cache.all_())
        self.assertEquals(SIZE, len(self.cache.all_()))
        self.assert_store_changes(self.store, updates=[obj])
        self.assertEquals(obj,self.cache[obj.attribute])

    def test_delete_adjustment(self):
        obj = LIST[SIZE/2]
        self.assertIn(obj,self.cache.all_())
        self.cache.delete(obj)
        self.assertNotIn(obj,self.cache.all_())
        self.assertEquals(SIZE-1, len(self.cache.all_()))
        self.assert_store_changes(self.store, deletes=[obj])
        self.assertIsNone(self.cache[obj.attribute])

    def test_iterator(self):
        self.assertEquals(set([o.attribute for o in LIST]),set(self.cache))

    def test_subtraction(self):
        self.store2 = helper.TestStore()
        self.cache2 = Facet(self.store2, 'attribute')
        common_obj = LIST[SIZE/2]
        uncommon_obj = TestObject()
        self.store2._all = set([common_obj, uncommon_obj])
        expected_set = set([attr for attr in self.cache if attr!=common_obj.attribute])
        self.assertEquals(expected_set, set(self.cache - self.cache2))
        self.assertEquals(set([uncommon_obj.attribute]), set(self.cache2 - self.cache))

    def test_intersection(self):
        self.store2 = helper.TestStore()
        self.cache2 = Facet(self.store2, 'attribute')
        common_obj = LIST[SIZE/2]
        uncommon_obj = TestObject()
        self.store2._all = set([common_obj, uncommon_obj])
        self.assertEquals(set([common_obj.attribute]), set(self.cache & self.cache2))
        self.assertEquals(set([common_obj.attribute]), set(self.cache2 & self.cache))



if __name__ == '__main__':
    unittest2.main()
