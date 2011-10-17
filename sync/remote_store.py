import logger
from base_store import BaseStore
from pprint import pformat
from pprint import pprint

# lots of assumption here:
  # 1) remote store returns no soft_delete items in its list-- not taking that possibility into account right now
  # 2) that you're able to create a full list of your remote entities -- #TODO make it possible to bring in changesets, or only thigns that might've changed since last sync, or partial list, or etc...?
  # 3) .... many others.. #TODO need to expand

class RemoteStore(BaseStore):
    local_existence_attribute = None

    def __init__(self):
        super(RemoteStore, self).__init__()
        self.local_existence_attribute = self.__class__.local_existence_attribute
        self.log = logger.get_log(self.__class__,'remote')

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
        self.log.debug('Inbound Upsert || Starting...')
        inserts = []
        updates = []
        possibles = self.cached_list()
        for obj in possibles:
            id_ = getattr(obj, self.key_attribute)
            merge_obj = merge_pile.get(self.key_attribute, id_)
            if merge_obj:
                if self.equals(merge_obj, obj):
                    self.log.debug('Inbound Update || Ignoring this object since all synchronizable fields already exist as an object on the merge pile...\nremote object:\n%s\nmerge-pile object:\n%s\n' % (pformat(vars(obj)), pformat(vars(merge_obj))))
                elif self.locally_updated_since_last_sync(merge_obj):
                    self.log.debug('Inbound Update || Ignoring this object because the corresponding merge-pile object appears to already have been updating since the last sync, and we want local changes to override in this case (cuz this library doesn\'t have the ability to sync at the attribute level right now)...\nremote object:\n%s\nmerge-pile object:\n%s\n' % (pformat(vars(obj)), pformat(vars(merge_obj))))
                else:
                    self.log.debug('Inbound Update || Updating existing merge-pile object with remote object...\nremote object:\n%s\nmerge-pile object:\n%s\n' % (pformat(vars(obj)), pformat(vars(merge_obj))))
                    self.merge_object(obj, merge_obj)
                    self.mark_updated(merge_obj)
                    updates.append(obj)
            else:
                self.log.debug('Inbound Insert || Creating new merge-pile object from remote object...\nremote_object:\n%s \n' % pformat(vars(obj)))
                merge_pile.add(obj)
                self.mark_updated(obj)
                inserts.append(obj)
        self.log.info('Inbound Upsert || Complete (screened:%s  merge-pile-updates:%s  merge-pile-inserts:%s)' % (len(possibles),len(updates),len(inserts)))

    def _inbound_delete(self, merge_pile):
        self.log.debug('Inbound Delete || Starting...')
        deletes = []
        missing_candidates = merge_pile.missing_objects(self.key_attribute, self.cached_hash().keys())
        for obj in missing_candidates:
            if self.local_existence(obj):
                self.log.debug('Inbound Delete || Deleting object on the merge-pile because it has already established local_existence with this remote store, and it no longer exists in the remote store...\nmerge-pile object:\n%s\n' % pformat(vars(obj)))
                self.mark_deleted(obj)
                deletes.append(obj)
            else:
                self.log.debug('Inbound Delete || Ignoring the presense of this object in the merge-pile and its absense in the remote store, because it hasn\'t established its presence yet with the remote store, and is likely going to cause a downstream create against the remote store on this very sync operation...\nmerge-pile object:\n%s\n' % pformat(vars(obj)))
        self.log.info('Inbound Delete || Complete (screened:%s  merge-pile-deletes:%s)' % (len(missing_candidates),len(deletes)))

    def _outbound_delete(self, merge_pile):
        self.log.debug('Outbound Delete || Starting...')
        deletes = []
        candidates = [o for o in merge_pile.common_objects(self.key_attribute, self.cached_hash().keys()) if self.local_deleted_at(o)]
        for obj in candidates:
            self.log.debug('Outbound Delete || Deleting object in the remote store because it has been soft deleted locally, and the remote store seems to think it still exists...\nmerge-pile object:\n%s\n' % pformat(vars(obj)))
            self.delete(obj)
            self.mark_deleted(obj)
            deletes.append(obj)
        self.log.info('Outbound Delete || Complete (screened:%s  merge-pile-deletes:%s)' % (len(candidates),len(deletes)))


    def _outbound_create(self, merge_pile):
        self.log.debug('Outbound Create || Starting...')
        creates = []
        candidates = merge_pile.missing_objects(self.key_attribute, self.cached_hash().keys())
        for obj in candidates:
            if self.local_existence(obj):
                self.log.error('Outbound Create || This shouldn\'t occur -- Ignoring this object since it seems to both exist and not exist in the remote, something\'s wrong!\nmerge-pile object:\n%s' % pformat(vars(obj)))
            elif self.local_deleted_at(obj):
                # this is fine and expected!  for incoming deletes we would've marked them as soft_deleted, and now they're getting picked up here
                self.log.debug('Outbound Create || Ignoring cuz this is just an incoming delete already dealt with...')
            else:
                print "================"
                pprint(vars(obj))
                self.merge_object(self.save(obj), obj)
                pprint(vars(obj))
                self.mark_updated(obj)
                try:
                    self.local_store.save(obj)
                    self.log.debug('Outbound Create || Creating new objects in the remote store from the merge-pile...\nmerge-pile object:\n%s \n' % pformat(vars(obj)))
                    creates.append(obj)
                except:
                    self.delete(obj)  # attempt to backtrack back into a sync state-- otherwise we'll get duplicates here
                    self.log.error('Outbound Create || Failed Attempt at Insert!  Attempting to back out to minimize damage...\nmerge-pile object:\n%s \n' % pformat(vars(obj)))
        self.log.info('Outbound Create || Complete (screened:%s  remote-creates:%s)' % (len(candidates),len(creates)))

    def _outbound_update(self, merge_pile):
        self.log.debug('Outbound Update || Starting...')
        updates = []
        candidates = merge_pile.common_objects(self.key_attribute, self.cached_hash().keys())
        for merged_obj in candidates:
            remote_obj = self.cached_hash()[getattr(merged_obj,self.key_attribute)]
            if self.local_deleted_at(merged_obj):
                self.log.error('Outbound Update || This shouldn\'t occur -- Ignoring this object since it seems to still exist in the remote even though it should\'ve been cleared by now!\nmerge-pile object:\n%s' % pformat(vars(merged_obj)))
            else:
                if self.equals(merged_obj, remote_obj):
                    self.log.debug('Outbound Update || Ignoring this object since all synchronizable fields already exist as an object in the remote store...\nremote object:\n%s\nmerge-pile object:\n%s\n' % (pformat(vars(remote_obj)), pformat(vars(merged_obj))))
                else:
                    self.save(merged_obj)
                    self.mark_updated(merged_obj)
                    self.log.debug('Outbound Update || Updating remote object with those attributes from the merge-pile...\nremote object:\n%s\nmerge-pile object:\n%s\n' % (pformat(vars(remote_obj)), pformat(vars(merged_obj))))
                    updates.append(merged_obj)
                    try:
                        self.local_store.save(merged_obj)
                    except:
                        self.save(remote_obj)  # attempt to backtrack back into a sync state-- otherwise we'll get duplicates here
                        self.log.error('Outbound Update || Failed Attempt at Insert!  Attempting to back out to minimize damage (There probably will be damage here-- need to revisit!)...\nremote object:\n%s\nmerge-pile object:\n%s\n' % (pformat(vars(remote_obj)), pformat(vars(merged_obj))))
        self.log.info('Outbound Update || Complete (screened:%s  remote-updates:%s)' % (len(candidates),len(updates)))
