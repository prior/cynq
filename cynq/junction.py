from cynq import logging_helper

REMOTE_STORE_FIELD_PROXIES = ['name', 'key']

class Junction(object):
    def __init__(self, local_store, remote_store):
        super(Junction, self).__init__()
        self.ls = local_store
        self.rs = remote_store
        self.rs.junction = self
        self._build_proxies()
        self.fatal_failure = None
        self.log = logging_helper.get_log('cynq.junction.%s' % self.name)

    def _build_proxies(self):
        for field in REMOTE_STORE_FIELD_PROXIES:
            setattr(self, field, getattr(self.rs, field))

    def key_value(self, obj): 
        return obj.get(self.key)

    #def _get_extra_undeleted_locals(self):
        #return (o for o in self.ls.list_ if not o.get('_deleted_at') and not o.get('_error') and o.get(self.key) not in self.ls_hash_)
    #extra_undeleted_locals = property(_get_extra_undeleted_locals)

    def local_create(self, remote_obj):
        local_obj = self.local_pullable_clone(remote_obj)
        self.ls.create(local_obj)
        return local_obj

    def local_update(self, local_obj, remote_obj):
        if self.remote_pushable_merge(remote_obj, local_obj):
            self.update_updated_at(local_obj)
            self.ls.update(local_obj)
        return local_obj

    def local_delete(self, local_obj, cynq_started_at):
        local_obj[self.ls.spec.soft_delete] = cynq_started_at



    def remote_create(self, local_obj):
        remote_obj = self.remote_pullable_clone(local_obj)
        remote_obj['_source'] = local_obj
        self.rs.create(remote_obj)
        return remote_obj

    def remote_update(self, remote_obj, local_obj):
        if self.remote_pullable_merge(local_obj, remote_obj):
            remote_obj['_source'] = local_obj
            self.rs.update(remote_obj)
        return remote_obj

    def remote_delete(self, remote_obj):
        self.rs.delete(remote_obj)
        return remote_obj





    def remote_pushable_clone(self, obj):
        return self.rs.pushable_clone(obj)

    def remote_pullable_clone(self, obj):
        return self.rs.pullable_clone(obj)

    def local_pushable_clone(self, obj):
        return self.remote_pullable_clone(self, obj)

    def local_pullable_clone(self, obj):
        return self.remote_pushable_clone(self, obj)

    def scoped_clone(self, obj):
        return self.rs.scoped_clone(obj)

    def remote_pushable_merge(self, source, target):
        return self.rs.pushable_merge(source, target)

    def remote_pullable_merge(self, source, target):
        return self.rs.pullable_merge(source, target)

    def relevant_object_errors(self, obj):
        error_keys = set([self.ls.name,self.rs.name]) & set(obj.get('_error',{}))
        return [obj[k] for k in error_keys]

    def _get_living_locals(self):
        return (o for o in self.ls.list_ if not o.get(self.ls.soft_delete))
    living_locals = property(_get_living_locals)

    def _get_valid_living_locals(self):
        return (o for o in self.ls.list_ if not o.get(self.ls.soft_delete) and not self.relevant_object_errors(o))
    valid_living_locals = property(_get_valid_living_locals)

    def _get_expected_valid_living_locals(self):
        return (o for o in self.valid_living_locals if self.ls.is_expected_remotely(o, self.name))
    expected_valid_living_locals = property(_get_expected_valid_living_locals)

    def _get_unexpected_valid_living_locals(self):
        return (o for o in self.valid_living_locals if not self.ls.is_expected_remotely(o, self.name))
    unexpected_valid_living_locals = property(_get_unexpected_valid_living_locals)
