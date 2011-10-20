import unittest2
from datetime import datetime
from datetime import timedelta
from cynq.controller import Controller
from cynq.test import helper
from sanetime.sanetime import SaneTime


class TestRemote1(helper.TestStore):
    communal_attributes = ['attr','extra']
    owned_attributes = ['owned1']
    key_attribute = 'attr'
    remote_expectation_attribute = 'remote1_expectation'

    def create(self, obj):
        obj = super(TestRemote1, self).create(obj)
        obj.change(['owned1'])
        return obj

class TestRemote2(helper.TestStore):
    communal_attributes = ['attr']
    owned_attributes = ['owned2']
    key_attribute = 'attr'
    remote_expectation_attribute = 'remote2_expectation'

    def create(self, obj):
        obj = super(TestRemote2, self).create(obj)
        obj.change(['owned2'])
        return obj

class TestLocal(helper.TestStore):
    communal_attributes = ['attr','owned1','owned2','extra','remote1_expectation', 'remote2_expectation']
    owned_attributes = ['id']

class TestObject(helper.TestObject):
    prepopulate_attributes = False 
    attrs = ['id','attr','owned1','owned2','extra']


class ControllerTest(helper.TestCase):

    def setUp(self):
        self.remote1_store = TestRemote1()
        self.remote2_store = TestRemote2()
        self.local_store = TestLocal()
        self.controller = Controller(self.local_store, [self.remote1_store, self.remote2_store])

    def tearDown(self):
        pass

    def test_sync(self):
        dt = SaneTime().to_naive_utc_datetime()
        self.remote1_store._all = [
            TestObject(attr='A', owned1='owned1-A', extra='extra1A'),
            TestObject(attr='B', owned1='owned1-B', extra='extra1B'),
            TestObject(attr='C', owned1='owned1-C', extra='extra1C'),
            TestObject(attr='D', owned1='owned1-D', extra='extra1D'), 
            TestObject(attr='E', owned1='owned1-E', extra='extra1E') ]
        self.remote2_store._all = [
            TestObject(attr='C', owned2='owned2-C'),
            TestObject(attr='D', owned2='owned2-D'), 
            TestObject(attr='E', owned2='owned2-E'),
            TestObject(attr='F', owned2='owned2-F') ]
        self.local_store._all = [
            TestObject(attr='B', owned1='owned1-B', owned2=None, extra='extra1B', deleted_at=dt, remote1_expectation=True, remote2_expectation=False, syncable_updated_at=dt, synced_at=dt),
            TestObject(attr='C', owned2='owned2-D', owned1=None, extra='extra3C', deleted_at=None, remote1_expectation=False, remote2_expectation=True, syncable_updated_at=dt+timedelta(1), synced_at=dt), 
            TestObject(attr='E', owned1=None, owned2=None, extra='extra3E', deleted_at=None, remote1_expectation=False, remote2_expectation=False, syncable_updated_at=dt, synced_at=dt),
            TestObject(attr='G', owned1='owned2-G', owned2=None, extra='extra3G', deleted_at=dt, remote1_expectation=True, remote2_expectation=False, syncable_updated_at=dt+timedelta(1), synced_at=dt) ]

        for o in self.local_store.all_():
            o.deleted_at

        self.controller.sync()



if __name__ == '__main__':
    unittest2.main()
