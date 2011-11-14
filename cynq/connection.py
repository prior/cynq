import logging_helper
from pprint import pformat
#from pprint import pprint


#TODO: need to clean up relationship with local and decouple more -- right now it is very coupled - warning-- sizeable task!
# model must have 'deleted_at', and 'exists_in_webinar' and 'exists_in_hubspot', and 'syncable_updated_at'

#TODO: need to think through more the implications of expecting the same object to come back around from the remote object
    #   definitely need to be able to incorporate extra info that comes back on creates, but should I really be expecting it to be the same exact object-- doesn't seem right
#TODO: need to guard against external outages, and trying to keep db consistent

#TODO: need to consider whether we'd only ever get info back on creaets-- currently designed to only look for info back on outbound creates-- need to document either way

#TODO: need to think about difference between a truly shared attribute that you can possible change
#         versus an attribute that is only reported on somewhere else, i.e. owned, shared, and
#         (audited? or reported? or logged? or something that designates this store cares and
#         records this particular value but will never be changing it -- right now that has to be
#         designated as 'shareable'
class Connection(object):
    def __init__(self, faceted_local, faceted_remote):
        super(Connection,self).__init__()
        self.local = faceted_local
        self.remote = faceted_remote
        self.log = logging_helper.get_log('cynq.connection')
        self.stats = {
            'local_reanimates':[], 
            'local_creates':[], 
            'local_updates':[], 
            'local_deletes':[],
            'remote_deletes':[],
            'remote_updates':[],
            'remote_creates':[] }

    def _local_reanimate(self, local_obj, remote_obj):
        change_dict = self.remote.change_dict_if_merge_readables(local_obj, remote_obj)
        previous_caring_dict = self.local.caring_dict(local_obj, self.remote.remote_expectation_attribute, 'deleted_at')
        self.remote.merge_readables(local_obj, remote_obj)
        local_obj.deleted_at=None
        self._set_remote_expectation(local_obj, True)
        self.stats['local_reanimates'].extend([self.local.key_attribute_value(local_obj)])
        self.log.debug(
            "local reanimate... ( remote=%s, changes=%s, previous_local=%s, final_local=%s )" % (
                self.remote,
                change_dict,
                previous_caring_dict,
                self.local.caring_dict(local_obj, self.remote.remote_expectation_attribute, 'deleted_at')))

    def _local_update(self, local_obj, remote_obj):
        previous_caring_dict = self.local.caring_dict(local_obj, self.remote.remote_expectation_attribute)
        change_dict = self.remote.change_dict_if_merge_readables(local_obj, remote_obj)
        self.remote.merge_readables(local_obj,remote_obj)
        self._set_remote_expectation(local_obj, True)
        self.stats['local_updates'].extend([self.local.key_attribute_value(local_obj)])
        self.log.debug(
            "local update... ( remote=%s, changes=%s, previous_local=%s, final_local=%s )" % (
                self.remote,
                change_dict,
                previous_caring_dict,
                self.local.caring_dict(local_obj, self.remote.remote_expectation_attribute)))

    def _local_create(self, remote_obj):
        change_dict = self.remote.caring_dict(remote_obj)
        local_obj = self.local.create(remote_obj)
        local_obj.deleted_at = local_obj.synced_at = local_obj.syncable_updated_at = None
        self._set_remote_expectation(local_obj, True)
        self.stats['local_creates'].extend([self.local.key_attribute_value(local_obj)])
        self.log.debug(
            "local create... ( remote=%s, changes=%s, final_local=%s )" % (
                self.remote,
                change_dict,
                self.local.caring_dict(local_obj, self.remote.remote_expectation_attribute)))

    def _local_delete(self, local_obj, synced_at):
        local_obj.deleted_at = synced_at
        self._set_remote_expectation(local_obj, False)
        self.stats['local_deletes'].extend([self.local.key_attribute_value(local_obj)])
        self.log.debug(
            "local delete... ( remote=%s, final_local=%s )" % (
                self.remote,
                self.local.caring_dict(local_obj, self.remote.remote_expectation_attribute, 'deleted_at')))

    def _remote_delete(self, local_obj, remote_obj):
        self.remote.delete(remote_obj)
        self._set_remote_expectation(local_obj, False)
        self.stats['remote_deletes'].extend([self.local.key_attribute_value(local_obj)])
        self.log.debug(
            "remote deleted... ( remote=%s, final_local=%s )" % (
                self.remote,
                self.local.caring_dict(local_obj, self.remote.remote_expectation_attribute, 'deleted_at')))

    def _remote_update(self, local_obj, remote_obj):
        change_dict = self.remote.change_dict_if_merge_writeables(remote_obj, local_obj)
        self.remote.update(self.remote.merge_writeables(remote_obj, local_obj))
        self._set_remote_expectation(local_obj, True)
        self.stats['remote_updates'].extend([self.local.key_attribute_value(local_obj)])
        self.log.debug(
            "remote update... ( remote=%s, changes=%s, final_remote=%s, final_local=%s )" % (
                self.remote,
                change_dict,
                self.remote.caring_dict(remote_obj),
                self.local.caring_dict(local_obj, self.remote.remote_expectation_attribute)))

    def _remote_create(self, local_obj):
        new_remote_obj = self.remote.create(local_obj)
        self.remote.merge_readables(local_obj, new_remote_obj)
        self._set_remote_expectation(local_obj, True)
        self.stats['remote_creates'].extend([self.local.key_attribute_value(local_obj)])
        self.log.debug(
            "remote create... ( remote=%s, final_remote=%s, final_local=%s )" % (
                self.remote,
                self.remote.caring_dict(new_remote_obj),
                self.local.caring_dict(local_obj, self.remote.remote_expectation_attribute)))

    def inbound_create_and_update(self):
        for key in self.remote:
            remote_obj = self.remote[key]
            if key in self.local:
                local_obj = self.local[key]
                if local_obj.deleted_at:  
                    if not self._has_remote_expectation(local_obj): #reanimate
                        self._local_reanimate(local_obj, remote_obj)
                else: 
                    if not self._has_local_changed_since_last_sync(local_obj): #update
                        if not self.remote.readables_seem_equal(local_obj, remote_obj) or not self._has_remote_expectation(local_obj): # only if diff
                            self._local_update(local_obj, remote_obj)
            else: #create
                self._local_create(remote_obj)

    def inbound_delete(self, synced_at):
        for local_key in (self.local - self.remote):
            local_obj = self.local[local_key]
            if not local_obj.deleted_at and self._has_remote_expectation(local_obj):
                self._local_delete(local_obj, synced_at)

    def outbound_delete(self):
        for key in (self.local & self.remote):
            local_obj = self.local[key]
            if local_obj.deleted_at and self._has_remote_expectation(local_obj):
                self._remote_delete(local_obj, self.remote[key])

    def outbound_create_and_update(self):
        for local_obj in (self.local.all_() + self.local.leftovers.values()): # include leftovers since we may also want to create them (in the case that the key isn't generated til they are created remotely)
            if not local_obj.deleted_at: 
                key = getattr(local_obj, self.remote.key_attribute, None)
                if key and key in self.remote: #update
                    remote_obj = self.remote[key]
                    if not self.remote.writeables_seem_equal(local_obj, remote_obj): # only if diff
                        self._remote_update(local_obj, remote_obj)
                else: 
                    if not self._has_remote_expectation(local_obj): #create
                        self._remote_create(local_obj)

    def _has_remote_expectation(self, local_obj):
        return getattr(local_obj, self.remote.remote_expectation_attribute, False)

    def _set_remote_expectation(self, obj, value=True):
        setattr(obj, self.remote.remote_expectation_attribute, value)

    def _has_local_changed_since_last_sync(self, local_obj):
        synced_at = local_obj.synced_at
        syncable_updated_at = local_obj.syncable_updated_at
        return synced_at and syncable_updated_at and syncable_updated_at > synced_at





