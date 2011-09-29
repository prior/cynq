import unittest2
import uuid
from datetime import datetime
import copy

from sync.remote_store import RemoteStore
from sync.local_store import LocalStore


def random_str():
    return str(uuid.uuid4())[:16]

class BaseTestStore(object):
    def __init__(self):
        self.hash_ = {}

    def _get(self, id_):
        return self.hash_[id_]

    def _list(self):
        return self.hash_.values()

    def _update(self, obj):
        if not self.get_id(obj, None):
            raise Exception("trying to update uncreated object")
        return self._core_save(obj)

    def _create(self, obj):
        for attr in self.owned_attributes:
            setattr(obj, attr, random_str())
        return self._core_save(obj)

    def _delete(self, obj):
        del self.hash_[self.get_id(obj)]
        return obj

    def _core_save(self, obj):
        self.hash_[self.get_id(obj)] = obj
        return obj

    def _core_delete(self, obj):
        del self.hash_[self.get_id(obj)]


class RemoteTestStore(BaseTestStore, RemoteStore):
    def __init__(self):
        BaseTestStore.__init__(self)
        RemoteStore.__init__(self)

    def conceive(self):
        kwargs = {}
        for attr in self.syncable_attributes:
            kwargs[attr] = random_str()
        return self._core_save(TestObject(**kwargs))


class LocalTestStore(BaseTestStore, LocalStore):
    def __init__(self):
        BaseTestStore.__init__(self)
        LocalStore.__init__(self)

    def _delete(self, obj):
        obj.deleted_at = datetime.utcnow()
        return obj

    def conceive(self):
        kwargs = {}
        syncable_and_not_owned_elsewhere = set(self.syncable_attributes+self.owned_attributes)
        for rs in self.remote_stores:
            for attr in rs.owned_attributes:
                syncable_and_not_owned_elsewhere.discard(attr)
        for attr in syncable_and_not_owned_elsewhere:
            kwargs[attr] = random_str()
        return self._core_save(TestObject(**kwargs))

    def seed(self, count=1, deleted_count=0):
        objects = []
        for i in xrange(0,count):
            o = TestObject.generate_random()
            if deleted_count:
                o.deleted_at = datetime.utcnow()
                deleted_count = deleted_count - 1
            else:
                for rs in self.remote_stores:
                    kwargs = {}
                    for attr in set(rs.owned_attributes+rs.syncable_attributes):
                        kwargs[attr]=getattr(o,attr,None)
                    rs._core_save(TestObject(**kwargs))
            objects.append(self._core_save(o))
        return objects


class PersonRemoteStore1(RemoteTestStore):
    syncable_attributes = ['remote_id1', 'email', 'name']
    owned_attributes = ['remote_id1']
    key_attribute = 'remote_id1'
    local_existence_attribute = 'remote_id1'

class PersonRemoteStore2(RemoteTestStore):
    syncable_attributes = ['remote_id2', 'extra_id2', 'email']
    owned_attributes = ['remote_id2', 'extra_id2']
    key_attribute = 'remote_id2'
    local_existence_attribute = 'remote_id2'

class PersonRemoteStore3(RemoteTestStore):
    syncable_attributes = ['email', 'address']
    owned_attributes = []
    key_attribute = 'email'
    local_existence_attribute = 'existence3'

class PersonLocalStore(LocalTestStore):
    syncable_attributes = ['remote_id1', 'remote_id2', 'extra_id2', 'email', 'name', 'address']
    owned_attributes = ['id_', 'local_info']
    key_attribute = 'id_'

class WebexRemoteEventStore(RemoteStore):
    syncable_attributes = ['remote_id', 'title','description','starts_at','duration']
    owned_attributes = ['remote_id']
    key_attribute = 'remote_id'

class LocalEventStore(RemoteStore):
    syncable_attributes = ['remote_id', 'title','description','starts_at','duration']
    owned_attributes = ['id']
    key_attribute = 'id'


class TestObject(object):
    attributes = ('id_','remote_id1','remote_id2','extra_id2','email','name','address','local_info','syncable_updated_at','existence3','deleted_at','synced_at')
    def __init__(self, **kwargs):
        for attr in self.__class__.attributes:
            kwargs.setdefault(attr, None)
        for k in kwargs:
            setattr(self,k,kwargs[k])

    @classmethod
    def generate_random(cls):
        kwargs = {}
        now = datetime.utcnow()
        for attr in cls.attributes:
            if attr.endswith('_at'):
                if attr == 'deleted_at':
                    kwargs[attr] = None
                else:
                    kwargs[attr] = now
            else:
                kwargs[attr] = random_str()
        return TestObject(**kwargs)

    def equals(self, other):
        return all([getattr(self, a, None) == getattr(other, a, None) for a in self.__class__.attributes])

    def __unicode__(self):
        return "email: %s" % self.email


class SyncTest(unittest2.TestCase):

    def setUp(self):
        self.rs1 = PersonRemoteStore1()
        self.rs2 = PersonRemoteStore2()
        self.ls = PersonLocalStore()
        self.ls.attach_remote_store(self.rs1)
        self.ls.attach_remote_store(self.rs2)

    def assert_synced(self):
        self.ls.sync_prep()
        self.ls.is_synced(testcase=self)

    def assert_not_synced(self):
        self.ls.sync_prep()
        self.ls.is_not_synced(testcase=self)
        
    def test_assert_synced(self):
        self.assert_synced()
        obj = self.ls._core_save(TestObject.generate_random())
        self.assert_not_synced()
        for rs in self.ls.remote_stores:
            rs._core_save(obj)
        self.assert_synced()
        obj = self.ls._core_save(TestObject.generate_random())
        self.assert_not_synced()
        obj.deleted_at = datetime.utcnow()
        self.assert_synced()

    def test_remote_store_equals(self):
        proto = self.rs1.conceive()
        self.assertTrue(self.rs1.equals(proto, self.rs1.get(proto.remote_id1)))

        # equals shouldn't care about things that aren't shared
        dup = copy.copy(proto)
        dup.random_crap = 'random_crap'
        self.assertTrue(self.rs1.equals(proto, dup))

        # equals should fail if we change something that sync controller is sharing
        dup = copy.copy(proto)
        dup.remote_id1 = 'somethingelse'
        self.assertFalse(self.rs1.equals(proto, dup))

    def test_seed(self):
        seeded_hash = dict((o.id_,o) for o in self.ls.seed(3))
        stored_hash = dict((o.id_,o) for o in self.ls.list_())

        # make sure stored and seeded are the same
        self.assertEquals(3,len(stored_hash))
        for id_ in stored_hash:
            self.assertTrue(stored_hash[id_].equals(seeded_hash[id_]))

        # make sure all the vitals are populated and we're completely in sync
        for obj in stored_hash.values():
            for attr in [a for s in [self.ls]+self.ls.remote_stores for a in s.owned_attributes]:
                self.assertTrue(getattr(obj,attr,None))
        self.assert_synced()

    def test_deleted_seed(self):
        seeded_hash = dict((o.id_,o) for o in self.ls.seed(5, deleted_count=3))
        stored_hash = dict((o.id_,o) for o in self.ls.list_())

        # make sure stored and seeded are the same
        self.assertEquals(5, len(stored_hash))
        delete_count = 0
        for id_ in stored_hash:
            self.assertTrue(stored_hash[id_].equals(seeded_hash[id_]))
            if stored_hash[id_].deleted_at:
                delete_count += 1
        self.assertEquals(3, delete_count)

        # make sure all the vitals are populated and we're completely in sync
        for obj in stored_hash.values():
            for attr in [a for s in [self.ls]+self.ls.remote_stores for a in s.owned_attributes]:
                self.assertTrue(getattr(obj,attr,None))
        self.assert_synced()


    def test_remote_emergence(self):
        seed_objs = self.ls.seed(1, deleted_count=1)
        self.assertEquals(1, len(seed_objs))
        obj = self.rs1.conceive()
        self.assert_not_synced()
        self.ls.sync()
        self.assert_synced()
        self.assertEquals(2,len(self.ls.list_()))
        self.assertTrue(self.rs1.equals(obj, self.rs1.cached_hash()[getattr(obj,self.rs1.key_attribute)]))

    def test_local_emergence(self):
        self.ls.seed(5, deleted_count=3)
        obj = self.ls.conceive()
        self.assert_not_synced()
        self.ls.sync()
        self.assert_synced()
        self.assertEquals(6,len(self.ls.list_()))
        self.assertTrue(self.ls.equals(obj, self.ls.cached_hash()[getattr(obj,self.ls.key_attribute)]))

    def test_remote_disappearance(self):
        seed_objs = self.ls.seed(5, deleted_count=3)
        delete_obj = seed_objs[-1]
        self.rs2.delete(delete_obj)
        self.assert_not_synced()
        self.ls.sync()
        self.assert_synced()
        self.assertEquals(5,len(self.ls.list_()))
        self.assertEquals(4,sum(not not o.deleted_at for o in self.ls.list_()))
        self.assertNotIn(self.rs2.get_id(delete_obj),self.rs2.cached_hash())

    def test_local_disappearance(self):
        seed_objs = self.ls.seed(5, deleted_count=3)
        delete_obj = seed_objs[-1]
        self.ls.delete(delete_obj)
        self.assert_not_synced()
        self.ls.sync()
        self.assert_synced()
        self.assertEquals(5,len(self.ls.list_()))
        self.assertNotIn(self.rs1.get_id(delete_obj),self.rs1.cached_hash())
        self.assertNotIn(self.rs2.get_id(delete_obj),self.rs2.cached_hash())

    def test_remote_changes(self):
        self.ls.seed(5, deleted_count=3)
        update_obj = self.rs1.list_()[-1]
        update_obj.email = random_str()
        self.rs1._core_save(update_obj)
        self.assert_not_synced()
        self.ls.sync()
        self.assert_synced()
        self.assertEquals(5,len(self.ls.list_()))

    def test_local_changes(self):
        self.ls.seed(5, deleted_count=3)
        update_obj = [o for o in self.ls.list_() if o.deleted_at is None][0]
        email = random_str()
        update_obj.email = email
        update_obj.syncable_updated_at = datetime.utcnow()
        self.ls._core_save(update_obj)
        self.assert_not_synced()
        self.ls.sync()
        self.assert_synced()
        self.assertEquals(5,len(self.ls.list_()))
        self.assertTrue(any(email==o.email for o in self.ls.list_()))


if __name__ == '__main__':
    unittest2.main()
