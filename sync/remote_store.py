from base_store import BaseStore

class RemoteStore(BaseStore):
    local_existence_attribute = None

    def __init__(self):
        super(RemoteStore, self).__init__()
        self.local_existence_attribute = self.__class__.local_existence_attribute

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
        for obj in self.cached_list():
            id_ = getattr(obj, self.key_attribute)
            merge_obj = merge_pile.get(self.key_attribute, id_)
            if merge_obj:
                if not self.equals(merge_obj, obj) and not self.locally_updated_since_last_sync(merge_obj):
                    self.merge_object(obj, merge_obj)
                    self.mark_updated(merge_obj)
            else:
                merge_pile.add(obj)
                self.mark_updated(obj)

    def _inbound_delete(self, merge_pile):
        for obj in merge_pile.missing_objects(self.key_attribute, self.cached_hash().keys()):
            if self.local_existence(obj):
                self.mark_deleted(obj)

    def _outbound_delete(self, merge_pile):
        for obj in merge_pile.common_objects(self.key_attribute, self.cached_hash().keys()):
            if self.local_deleted_at(obj):
                self.delete(obj)
                self.mark_deleted(obj)

    def _outbound_create(self, merge_pile):
        for obj in merge_pile.missing_objects(self.key_attribute, self.cached_hash().keys()):
            if not self.local_existence(obj) and not self.local_deleted_at(obj):
                self.merge_object(self.save(obj), obj)
                self.mark_updated(obj)
                try:
                    self.local_store.save(obj)
                except:
                    self.delete(obj)  # attempt to backtrack back into a sync state-- otherwise we'll get duplicates here

    def _outbound_update(self, merge_pile):
        for merged_obj in merge_pile.common_objects(self.key_attribute, self.cached_hash().keys()):
            remote_obj = self.cached_hash()[getattr(merged_obj,self.key_attribute)]
            if not self.local_deleted_at(merged_obj):
                if not self.equals(merged_obj, remote_obj):
                    self.save(merged_obj)
                    self.mark_updated(merged_obj)
                    try:
                        self.local_store.save(merged_obj)
                    except:
                        self.save(remote_obj)  # attempt to backtrack back into a sync state-- otherwise we'll get duplicates here

