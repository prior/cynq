from cynq.store.base import BaseStore

FIELD_PROXIES = ['id_', 'createable', 'updateable', 'deleteable', 'pushed', 'pulled', 'shared', 'key', 'since']

class RemoteStore(BaseStore):
    def __init__(self, remote_spec):
        super(RemoteStore,self).__init__(self, remote_spec)  #_TODO: ensure that spec passed is a remote spec
        self._build_spec_proxies()
        self._hash = None

    def _force_get_list(self):
        if not self.since:
            return super(RemoteStore,self)._force_get_list()
        locals_ = self.junction_valid_locals_expected_remotely
        since_cutoff = max(o.get(self.since) for o in locals_)
        lt_since = [o for o in locals_ if o.get(self.since) and o[self.since] < since_cutoff]
        return self.bulk_copy(lt_since) + self.all_(since=since_cutoff)

    def _build_spec_proxies(self):
        for field in FIELD_PROXIES:
            setattr(self, field, getattr(self.spec, field))

    def pushable_clone(self, obj):
        return self._copy(obj, self.pushed + self.shared)

    def pullable_clone(self, obj):
        return self._copy(obj, self.pulled + self.shared)

    def scoped_clone(self, obj):
        return self._clone(obj, self.pushed + self.pulled + self.shared)

    def _clone(self, obj, attrs):
        return dict((a, obj.get(a)) for a in attrs)

    def bulk_scoped_clone(self, objs):
        return (self.scoped_clone(o) for o in objs)


    #def writeablely_clone(self, obj):
        #return dict((attr, obj.get(attr)) for attr in (self.writeables))

    #def is_writeably_different(self, obj):
        #return any((for attr in 

    #def _get_writeables(self):
        #return self.shared + self.pulled
    #writeables = property(_get_writeables)

    def _get_hash(self):
        return self.get_hash(self.key)
    hash_ = property(_get_hash)

