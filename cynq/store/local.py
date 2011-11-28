from cynq.store.base import BaseStore


class LocalStore(BaseStore):
    SPEC_FIELD_PROXIES = ('name', 'createable', 'updateable', 'deleteable', 'pushed', 'key', 'soft_delete', 'expected_format', 'synced_at', 'syncable_updated_at')

    def __init__(self, local_spec):
        super(LocalStore,self).__init__(local_spec)

    def is_expected_remotely(self, remote_name, local_obj):
        return local_obj.get(self.expected_format % {'name':remote_name}, False)

    def set_expected_remotely(self, remote_name, local_obj, value=True):
        if bool(self.is_expected_remotely(remote_name, local_obj)) != bool(value):
            local_obj[self.expected_format % {'name':remote_name}] = value
            self.update(local_obj)

    ## force new dates on updated/created stuff
    #def paint_pending_changes(self, cynq_started_at):
        #for obj in (self._queued['updates'] + self._queued['creates']):
            #obj[self.spec.synced_at] = cynq_started_at
            #obj[self.spec.syncable_updated_at] = cynq_started_at


    def touched_syncables(self, local_obj, cynq_started_at):
        self.synced(local_obj, cynq_started_at)
        local_obj[self.spec.syncable_updated_at] = cynq_started_at

    def synced(self, local_obj, cynq_started_at):
        local_obj[self.spec.synced_at] = cynq_started_at
