from datetime import datetime
from base_store import BaseStore
from merge_pile import MergePile

class LocalStore(BaseStore):
    synced_at_attribute = 'synced_at'
    deleted_at_attribute = 'deleted_at'
    syncable_updated_at_attribute = 'syncable_updated_at'

    def __init__(self):
        super(LocalStore,self).__init__()
        self.synced_at_attribute = self.__class__.synced_at_attribute
        self.deleted_at_attribute = self.__class__.deleted_at_attribute
        self.syncable_updated_at_attribute = self.__class__.syncable_updated_at_attribute
        self.remote_stores = []

    def attach_remote_store(self, remote_store):
        remote_store.local_store = self
        remote_store.local_synced_at_attribute = self.synced_at_attribute
        remote_store.local_deleted_at_attribute = self.deleted_at_attribute
        remote_store.syncable_updated_at_attribute = self.syncable_updated_at_attribute
        self.remote_stores.append(remote_store)

    def sync_prep(self):
        self.sync_time = datetime.utcnow()
        super(LocalStore,self).sync_prep(self.sync_time)
        for rs in self.remote_stores:
            rs.sync_prep(self.sync_time)

    def sync(self):
        self.sync_prep()
        unique_keys = list(set([r.key_attribute for r in self.remote_stores]))
        merge_pile = MergePile(self.list_(), unique_keys) 
        for inbound_action in ['upsert','delete']:
            for rs in self.remote_stores:
                getattr(rs,'_inbound_%s' % inbound_action)(merge_pile)
        merge_pile.persist_changes(self)
        for outbound_action in ['delete','create','update']:
            for rs in self.remote_stores:
                getattr(rs,'_outbound_%s' % outbound_action)(merge_pile)

    # probably only for testing -- attempted to make this useful with asserts and non-asserting alike
    def is_synced(self, testcase=None):
        local_objs = self.list_()
        viable_objs = [o for o in local_objs if not getattr(o, self.deleted_at_attribute, None)]
        viable_count = len(viable_objs)
        for rs in self.remote_stores:
            remote_hash = dict((rs.get_id(o),o) for o in rs.list_())
            local_hash = dict((rs.get_id(o),o) for o in viable_objs if rs.get_id(o,None))
            if testcase:
                testcase.assertEquals(viable_count, len(local_hash))
                testcase.assertEquals(viable_count, len(remote_hash))
                testcase.assertEquals(0, len(set(local_hash).symmetric_difference(remote_hash)))
            else:
                expected_local_count = viable_count == len(local_hash)
                expected_remote_count = viable_count == len(remote_hash)
                expected_no_extras = 0 == len(set(local_hash).symmetric_difference(remote_hash))
                if not (expected_local_count and expected_remote_count and expected_no_extras):
                    return False
            for id_ in local_hash:
                expected_equality = rs.equals(local_hash[id_],remote_hash[id_])
                if testcase:
                    testcase.assertTrue(expected_equality)
                elif not expected_equality:
                    return False
        return True

    def is_not_synced(self, testcase=None):
        if testcase:
            testcase.assertFalse(self.is_synced())
        else:
            return not self.is_synced()

    def equals(self, local_obj1, local_obj2):
        attrs = set(self.syncable_attributes + self.owned_attributes) - set(a for rs in self.remote_stores for a in rs.owned_attributes)
        return all([getattr(local_obj1,attr) == getattr(local_obj2,attr) for attr in attrs])

