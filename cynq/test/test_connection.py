import unittest2
import uuid
from datetime import datetime
from cynq.connection import Connection
from cynq.stores.facet import Facet
from cynq.test import helper


class TestRemote(helper.TestStore):
    communal_attributes = ['attrL','attrM']
    owned_attributes = ['ownedB','ownedC']
    key_attribute = 'keyA'
    remote_existence_attribute = 'remote_existence'

class TestLocal(helper.TestStore):
    communal_attributes = ['keyA','ownedB','ownedC','attrL','attrM','attrN','remote_existence']
    owned_attributes = ['id']

class TestObject(helper.TestObject):
    prepopulate_attributes = True
    attrs = ['id','keyA','ownedB','ownedC','attrL','attrM','attrN','remote_existence']

SIZE = 4
LIST = [TestObject() for i in xrange(0,SIZE)]

class ConnectionTest(helper.TestCase):

    def setUp(self):
        self.remote_store = TestRemote()
        self.remote = Facet(self.remote_store, 'keyA')
        self.local_store = TestLocal()
        self.local = Facet(self.local_store, 'keyA')
        self.conn = Connection(self.local, self.remote, datetime.utcnow())

    def tearDown(self):
        pass

    def test_single_inbound_create_into_empty_local(self):
        obj = TestObject(TestRemote.understood_attributes())
        self.remote_store._all = [obj]
        self.assertEquals(set([obj]), self.remote.all_())
        self.assertEquals(set([obj]), self.local.all_())
        self.conn.inbound_create()
        self.assertEquals(set([obj]), self.remote.all_())
        self.assertEquals(set([obj]), self.local.all_())
        

if __name__ == '__main__':
    unittest2.main()
