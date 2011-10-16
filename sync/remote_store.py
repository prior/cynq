import logging_helper
from base_store import BaseStore

class RemoteStore(BaseStore):
    local_existence_attribute = None

    def __init__(self):
        super(RemoteStore, self).__init__()
        self.local_existence_attribute = self.__class__.local_existence_attribute
        self.logger = logging_helper.get_package_logger()

    def equals(self, obj1, obj2):
        if sum([getattr(obj1,attr) != getattr(obj2,attr) for attr in self.syncable_attributes]) == 0:
            return True
        return False

    def merge_object(self, from_object, to_object):
        for attr in self.syncable_attributes:
            setattr(to_object, attr, getattr(from_object, attr, None))

    def mark_updated(self, local_obj):
        setattr(local_obj, self.syncable_updated_at_attribute, self.sync_time)
        setattr(local_obj, self.local_synced_at_attribute, self.sync_time)
        local_obj._updated = True
        return local_obj

    def mark_deleted(self, local_obj):
        setattr(local_obj, self.local_existence_attribute, None)
        for attr in self.owned_attributes:
            setattr(local_obj, attr, None)
        if not self.local_deleted_at(local_obj):
            setattr(local_obj, self.local_deleted_at_attribute, self.sync_time)
        self.mark_updated(local_obj)

    def local_deleted_at(self, local_obj):
        return getattr(local_obj, self.local_deleted_at_attribute)

    def syncable_updated_at(self, local_obj):
        return getattr(local_obj, self.syncable_updated_at_attribute)

    def local_synced_at(self, local_obj):
        return getattr(local_obj, self.local_synced_at_attribute)

    def local_existence(self, local_obj):
        return getattr(local_obj, self.local_existence_attribute)

    def locally_updated_since_last_sync(self, local_obj):
        _syncable_updated_at = self.syncable_updated_at(local_obj)
        _local_synced_at = self.local_synced_at(local_obj)
        if getattr(local_obj,'_updated', None):
            return True
        return (not _local_synced_at and _syncable_updated_at) or (_local_synced_at and _syncable_updated_at and _syncable_updated_at > _local_synced_at)

    def _inbound_upsert(self, merge_pile):
        inserts = {}
        updates = {}
        print '=== inbound upsert staring for %s...' % self.__class__
        for obj in self.cached_list():
            id_ = getattr(obj, self.key_attribute)
            merge_obj = merge_pile.get(self.key_attribute, id_)
            if merge_obj:
                if not self.equals(merge_obj, obj) and not self.locally_updated_since_last_sync(vars(merge_obj)):
                    self.logger.debug('inbound update: updating existing merge-pile object...\n  target:%s\n  source:%s\n'%(merge_obj,vars(obj)))
                    print '===== inbound update: updating existing merge-pile object with remote object...\n  target:%s\n  source:%s\n'%(vars(merge_obj),vars(obj))
                    self.merge_object(obj, merge_obj)
                    self.mark_updated(merge_obj)
                    updates[id_] = obj
            else:
                self.logger.debug('inbound upsert: inserting new object to merge-pile: %s'%obj)
                print '===== inbound insert: inserting new object to merge-pile from remote object...\n  obj:%s'%vars(obj)
                merge_pile.add(obj)
                self.mark_updated(obj)
                inserts[id_] = obj
        self.logger.info('inbound upsert:  screened:%s  merge-pile-updates:%s  merge-pile-inserts:%s'%(len(self.cached_list()),len(updates),len(inserts)))
        print '=== inbound upsert:  screened:%s  merge-pile-updates:%s  merge-pile-inserts:%s'%(len(self.cached_list()),len(updates),len(inserts))

    def _inbound_delete(self, merge_pile):
        deletes = {}
        print '=== inbound delete starting for %s...' % self.__class__
        missing_candidates = merge_pile.missing_objects(self.key_attribute, self.cached_hash().keys())
        for obj in missing_candidates:
            if self.local_existence(obj):
                print '===== inbound delete: deleting object that exists on the merge-pile cuz I could find no record of it on the remote end...\n obj:%s'%vars(obj)
                self.mark_deleted(obj)
                deletes[getattr(obj, self.key_attribute)] = obj
        print '=== inbound delete:  screened:%s  merge-pile-deletes:%s'%(len(missing_candidates),len(deletes))

    def _outbound_delete(self, merge_pile):
        deletes = {}
        print '=== outbound delete starting for %s...' % self.__class__
        candidates = merge_pile.common_objects(self.key_attribute, self.cached_hash().keys())
        for obj in candidates:
            if self.local_deleted_at(obj):
                print '===== outbound delete: deleting object that has been soft deleted locally and still exists remotely...\n obj:%s'%vars(obj)
                self.delete(obj)
                self.mark_deleted(obj)
                deletes[getattr(obj, self.key_attribute)] = obj
        print '=== outbound delete:  screened:%s  merge-pile-deletes:%s'%(len(candidates),len(deletes))


    def _outbound_create(self, merge_pile):
        creates = []
        print '=== outbound create starting for %s...' % self.__class__
        candidates = merge_pile.missing_objects(self.key_attribute, self.cached_hash().keys())
        for obj in candidates:
            if not self.local_existence(obj) and not self.local_deleted_at(obj):
                self.merge_object(self.save(obj), obj)
                self.mark_updated(obj)
                try:
                    self.local_store.save(obj)
                    print '===== outbound insert: inserting new object to remote system from merge-pile...\n  obj:%s'%vars(obj)
                    creates.append(obj)
                except:
                    self.delete(obj)  # attempt to backtrack back into a sync state-- otherwise we'll get duplicates here
                    print '===== outbound insert: backtrack!'
        print '=== outbound create:  screened:%s  inserts:%s'%(len(candidates),len(creates))

    def _outbound_update(self, merge_pile):
        updates = []
        print '=== outbound update starting for %s...' % self.__class__
        #for merged_obj in merge_pile.common_objects(self.key_attribute, self.cached_hash().keys()):
        #self.logger("Outbound Update")
        candidates = merge_pile.common_objects(self.key_attribute, self.cached_hash().keys())
        for merged_obj in candidates:
            remote_obj = self.cached_hash()[getattr(merged_obj,self.key_attribute)]
            if not self.local_deleted_at(merged_obj):
                if not self.equals(merged_obj, remote_obj):
                    print '===== outbound update: updating existing remote object from merge-pile...\n  target:%s\n  source:%s\n'%(vars(remote_obj),vars(merged_obj))
                    updates.append(merged_obj)
                    self.save(merged_obj)
                    self.mark_updated(merged_obj)
                    try:
                        self.local_store.save(merged_obj)
                    except:
                        self.save(remote_obj)  # attempt to backtrack back into a sync state-- otherwise we'll get duplicates here
                        print '===== outbound update: backtrack!'
        print '=== outbound update:  screened:%s  updates:%s'%(len(candidates),len(updates))
