import unittest2
from datetime import datetime
from cynq.connection import Connection
from cynq.stores.facet import Facet
from cynq.test import helper


class TestRemote(helper.TestStore):
    communal_attributes = ['attr']
    owned_attributes = ['owned']
    key_attribute = 'key'
    remote_expectation_attribute = 'remote_expectation'

class TestLocal(helper.TestStore):
    communal_attributes = ['key','owned','attr','extra','remote_expectation']
    owned_attributes = ['id']

class TestObject(helper.TestObject):
    prepopulate_attributes = True
    attrs = ['id','key','owned','attr','extra','remote_expectation','deleted_at']

SIZE = 4
LIST = [TestObject() for i in xrange(0,SIZE)]

class ConnectionTest(helper.TestCase):

    def setUp(self):
        self.remote_store = TestRemote()
        self.remote = Facet(self.remote_store, 'key')
        self.local_store = TestLocal()
        self.local = Facet(self.local_store, 'key')
        self.conn = Connection(self.local, self.remote, datetime.utcnow())

    def tearDown(self):
        pass

    def materialize_local_obj(self, deleted_at=None, remote_expectation=False):
        return TestObject(*TestLocal.understood_attributes, deleted_at=deleted_at, remote_expectation=remote_expectation)

    def materialize_remote_obj(self, deleted_at=None, remote_expectation=False):
        return TestObject(*TestRemote.understood_attributes(), **{TestRemote.remote_expectation_attribute: False})

    def test_single_inbound_create_into_empty_local(self):
        obj = self.materialize_remote_obj()
        self.remote_store._all = [obj]

        self.assertFalse(obj.remote_expectation)
        self.conn.inbound_create()
        self.assertEquals(set([obj]), self.remote.all_())
        self.assertEquals(set([obj]), self.local.all_())
        self.assertTrue(obj.remote_expectation)
        self.assertIsNone(obj.deleted_at)

    def test_single_inbound_reanimate_into_single_deleted_local(self):
        remote_obj = TestObject(*TestRemote.understood_attributes())
        local_obj = TestObject(*TestLocal.understood_attributes(), deleted_at=datetime.utcnow(), remote_expectation=None, key=remote_obj.key)
        self.remote_store._all = set([remote_obj])
        self.local_store._all = set([local_obj])

        self.assertFalse(local_obj.remote_expectation)
        self.assertIsNotNone(local_obj.deleted_at)
        self.conn.inbound_create()
        self.assertEquals(set([remote_obj]), self.remote.all_())
        self.assertEquals(set([local_obj]), self.local.all_())
        self.assertTrue(local_obj.remote_expectation)
        self.assertIsNone(local_obj.deleted_at)
        

if __name__ == '__main__':
    unittest2.main()
