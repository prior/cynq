import unittest2
from cynq.stores.multi_facet import MultiFacet
from cynq.test import helper


class TestObject(helper.TestObject):
    prepopulate_attributes = True
    attrs = ['attr1','attr2']

SIZE = 4
LIST = [TestObject() for i in xrange(0,SIZE)]


class MultiFacetTest(helper.TestCase):

    def setUp(self):
        self.store = helper.TestStore()
        self.multi_facet = MultiFacet(self.store)
        self.store._all = set(LIST)
        self.facet1 = self.multi_facet.get_facet('attr1')
        self.facet2 = self.multi_facet.get_facet('attr2')

    def tearDown(self):
        pass

    def test_basics(self):
        for obj in LIST:
            self.assertIn(obj.attr1, self.facet1)
            self.assertNotIn(obj.attr2, self.facet1)
            self.assertIn(obj.attr2, self.facet2)
            self.assertNotIn(obj.attr1, self.facet2)

    def test_facet_creates(self):
        obj = TestObject()
        self.assertNotIn(obj.attr1, self.facet1)
        self.assertNotIn(obj.attr2, self.facet2)
        self.facet1.create(obj)
        self.assertIn(obj.attr1, self.facet1)
        self.assertIn(obj.attr2, self.facet2)
        self.assertEquals(obj, self.facet1[obj.attr1])
        self.assertEquals(obj, self.facet2[obj.attr2])
        self.assert_store_changes(self.store, creates=[obj], all_calls=1)

    def test_facet_updates(self):
        obj = LIST[SIZE/2]
        obj.change('attr3')
        self.assertIn(obj.attr1, self.facet1)
        self.assertIn(obj.attr2, self.facet2)
        self.facet1.update(obj)
        self.assertIn(obj.attr1, self.facet1)
        self.assertIn(obj.attr2, self.facet2)
        self.assertEquals(obj, self.facet1[obj.attr1])
        self.assertEquals(obj, self.facet2[obj.attr2])
        self.assert_store_changes(self.store, updates=[obj], all_calls=1)

    def test_facet_deletes(self):
        obj = LIST[SIZE/2]
        self.assertIn(obj.attr1, self.facet1)
        self.assertIn(obj.attr2, self.facet2)
        self.assertEquals(obj, self.facet1[obj.attr1])
        self.assertEquals(obj, self.facet2[obj.attr2])
        self.facet1.delete(obj)
        self.assertNotIn(obj.attr1, self.facet1)
        self.assertNotIn(obj.attr2, self.facet2)
        self.assertIsNone(self.facet1[obj.attr1])
        self.assertIsNone(self.facet2[obj.attr2])
        self.assert_store_changes(self.store, deletes=[obj], all_calls=1)


if __name__ == '__main__':
    unittest2.main()
