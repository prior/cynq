
#TODO: need to clean up relationship with local and decouple more -- right now it is very coupled - warning-- sizeable task!
# model must have 'deleted_at', and 'exists_in_webinar' and 'exists_in_hubspot', and 'syncable_updated_at'
class Connection(object):
    def __init__(self, faceted_local, faceted_remote, synced_at):
        super(Connection,self).__init__()
        self.local = faceted_local
        self.remote = faceted_remote
        self.synced_at = synced_at

    def inbound_create(self):
        for key in self.remote:
            remote_obj = self.remote[key]
            if key not in self.local:
                self._set_remote_expectation(remote_obj, True)
                self.local_create(remote_obj)
            else:  #looking for reanimate possibility
                local_obj = self.local[key]
                if local_obj.deleted_at and not self._has_remote_expectation(local_obj):
                    self.merge_object(local_obj, self.remote[key])
                    local_obj.deleted_at=None
                    self._set_remote_expectation(local_obj, True)

    def inbound_update(self):
        for local_key in (self.local & self.remote):
            local_obj = self.local[local_key]
            if not local_obj.deleted_at and not self._has_local_changed_since_last_sync(local_obj):
                remote_obj = self.remote[local_key]
                self.log.debug('Updating object in local cache...')
                self.merge_object(local_obj,remote_obj)

    def inbound_delete(self):
        for local_key in (self.local - self.remote):
            local_obj = self.local[local_key]
            if not local_obj.deleted_at and self._has_remote_expectation(local_obj):
                self.log.debug('Deleting local object...')
                self.local_delete(local_obj)

    def outbound_delete(self):
        for local_key in (self.local & self.remote):
            local_obj = self.local[local_key]
            if local_obj.deleted_at and self._has_remote_expectation(local_obj):
                self.log.debug('Deleting remote object...', local_obj=local_obj)
                self.remote_delete(local_obj)

    def outbound_update(self):
        for local_obj in (self.local & self.remote):
            if not local_obj.deleted_at:
                self.log.debug('Updating remote object...')
                self.remote_update(local_obj)

    def outbound_create(self):
        for local_obj in (self.local - self.remote):
            if not local_obj.deleted_at and not self._has_remote_expectation(local_obj):
                self.log.debug('Creating remote object...')
                self._set_remote_expectation(local_obj, True)
                self.local_update(self.remote_create(local_obj))


    def local_create(self, obj):
        self._set_remote_expectation(obj, True)
        return self.local.create(obj)

    def local_update(self, obj):
                self._set_remote_expectation(local_obj, True)
        return self.local.update(obj)

    def local_delete(self, obj):
        self._set_remote_expectation(obj, False)
        obj.deleted_at = self.synced_at
        return self.local.update(obj)

    #TODO: need to think through more the implications of expecting the same object to come back around from the remote object
       #   definitely need to be able to incorporate extra info that comes back on creates, but should I really be expecting it to be the same exact object-- doesn't seem right
    #TODO: need to guard against external outages, and trying to keep db consistent
    def remote_delete(self, obj):
        obj = self.remote.delete(obj)
        self._set_remote_expectation(obj, False)
        return self.local.update(obj)

    def remote_update(self, obj):
        self.remote.update(obj)
        self._set_remote_expectation(obj, True)
        return self.local.update(obj)

    def remote_create(self, obj):
        obj = self.remote.create(obj)
        self._set_remote_expectation(obj, True)
        return self.local.update(obj)

    def _has_remote_expectation(self, local_obj):
        return getattr(local_obj, self.remote.remote_expectation_attribute)

    def _set_remote_expectation(self, obj, value=False):
        setattr(obj, self.remote.remote_expectation_attribute, True)

    def _has_local_changed_since_last_sync(self, local_obj):
        synced_at = local_obj.synced_at
        syncable_updated_at = local_obj.syncable_updated_at
        return synced_at and syncable_updated_at and syncable_updated_at > synced_at

    def merge_object(self, target, source):
        for attr in self.remote.syncable_attributes + [self.remote.remote_expectation_attribute]:
            setattr(target, attr, getattr(source, attr, None))
        return target




