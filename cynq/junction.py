from cynq import logging_helper


REMOTE_STORE_FIELD_PROXIES = ['id_', 'key']

class Junction(object):
    def __init__(self, local_store, remote_store):
        super(Junction, self).__init__()
        self.ls = local_store
        self.rs = remote_store
        self.rs.junction = self
        self._build_proxies()
        self.fatal_failure = None
        self.log = logging_helper.get_log('cynq.junction.%s' % self.id_)

    def _build_proxies(self):
        for field in REMOTE_STORE_FIELD_PROXIES:
            setattr(self, field, getattr(self.remote_store, field))

    def key_value(self, obj): 
        return obj.get(self.key)

    #def _get_extra_undeleted_locals(self):
        #return (o for o in self.ls.list_ if not o.get('_deleted_at') and not o.get('_error') and o.get(self.key) not in self.ls_hash_)
    #extra_undeleted_locals = property(_get_extra_undeleted_locals)

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





    def _get_living_locals(self):
        return (o for o in self.ls.list_ if not o.get('_deleted_at'))
    living_locals = property(_get_living_locals)

    def _get_valid_living_locals(self):
        return (o for o in self.ls.list_ if not o.get('_deleted_at') and not o.get('_error'))
    valid_living_locals = property(_get_valid_living_locals)

    def _get_expected_valid_living_locals(self):
        return (o for o in self.valid_living_locals if self.ls.is_expected_remotely(o, self.id_))
    expected_valid_living_locals = property(_get_expected_valid_living_locals)

