import unittest2
import uuid
from cynq.stores.multi_facet import MultiFacet
from cynq.stores.base import Base


class TestRemote1(Remote):
    communal_attributes = ['attrB','attrC']
    owned_attributes = ['owned1']
    key_attribute = 'attrA'
    remote_existence_attribute = 'remote1_existence'

class Remote(base.Base):
    communal_attributes = []
    owned_attributes = []
    key_attribute = None
    remote_expectation_attribute = None

    def __init__(self, store):
        super(Remote, self).__init__()

    def list_(self):
        raise NotImplementedError()

    def update(self, obj):
        raise NotImplementedError()

    def create(self, obj):
        raise NotImplementedError()

    def delete(self, obj):
        raise NotImplementedError()
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
        self.attr1 = str(uuid.uuid4())[:16]
        self.attr2 = str(uuid.uuid4())[:16]

LIST_SIZE = 4

class MultiFacetTest(unittest2.TestCase):

    def setUp(self):
        self.test_store = TestStore()
        self.multi_facet = MultiFacet(self.test_store)
        self.test_list = [TestObject() for i in xrange(0,LIST_SIZE)]
        self.test_store._list = self.test_list

    def tearDown(self):
        pass

    def test_facet_creates(self):
        facet1 = self.multi_facet.get_facet('attr1')
        facet2 = self.multi_facet.get_facet('attr2')
        obj = self.test_list[LIST_SIZE/2]
        self.assertIn(obj.attr1,facet1)
        self.assertIn(obj.attr2,facet2)

        obj = TestObject()
        self.assertNotIn(obj.attr1,facet1)
        self.assertNotIn(obj.attr2,facet2)
        facet1.create(obj)
        self.assertIn(obj.attr1,facet1)
        self.assertIn(obj.attr2,facet2)
        self.assertEquals(obj,facet1[obj.attr1])
        self.assertEquals(obj,facet2[obj.attr2])
        self.assertEquals([obj],self.test_store.creates)

    def test_facet_updates(self):
        facet1 = self.multi_facet.get_facet('attr1')
        facet2 = self.multi_facet.get_facet('attr2')
        obj = self.test_list[LIST_SIZE/2]

        obj.attr3 = str(uuid.uuid4())[:16]
        self.assertIn(obj.attr1,facet1)
        self.assertIn(obj.attr2,facet2)
        facet1.update(obj)
        self.assertIn(obj.attr1,facet1)
        self.assertIn(obj.attr2,facet2)
        self.assertEquals(obj,facet1[obj.attr1])
        self.assertEquals(obj,facet2[obj.attr2])
        self.assertEquals([obj],self.test_store.updates)

    def test_facet_deletes(self):
        facet1 = self.multi_facet.get_facet('attr1')
        facet2 = self.multi_facet.get_facet('attr2')
        obj = self.test_list[LIST_SIZE/2]
        self.assertIn(obj.attr1,facet1)
        self.assertIn(obj.attr2,facet2)
        self.assertEquals(obj,facet1[obj.attr1])
        self.assertEquals(obj,facet2[obj.attr2])
        facet1.delete(obj)
        self.assertNotIn(obj.attr1,facet1)
        self.assertNotIn(obj.attr2,facet2)
        self.assertIsNone(facet1[obj.attr1])
        self.assertIsNone(facet2[obj.attr2])
        self.assertEquals([obj],self.test_store.deletes)


if __name__ == '__main__':
    unittest2.main()
