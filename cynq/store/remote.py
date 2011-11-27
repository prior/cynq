from cynq.store import BaseStore


class RemoteStore(BaseStore):
    SPEC_FIELD_PROXIES = ('name', 'createable', 'updateable', 'deleteable', 'pushed', 'pulled', 'shared', 'key', 'since')

    def __init__(self, remote_spec):
        super(RemoteStore,self).__init__(remote_spec)  #_TODO: ensure that spec passed is a remote spec
        self.clear_caches()

    def _force_get_list(self):
        if not self.since:
            return super(RemoteStore,self)._force_get_list()
        locals_ = self.junction_valid_locals_expected_remotely
        since_cutoff = max(o.get(self.since) for o in locals_)
        lt_since = [o for o in locals_ if o.get(self.since) and o[self.since] < since_cutoff]
        return self.bulk_copy(lt_since) + self.all_(since=since_cutoff)

    def pushable_clone(self, obj):
        return self._clone(obj, self.pushables)

    def pullable_clone(self, obj):
        return self._clone(obj, self.pullables)

    def scoped_clone(self, obj):
        return self._clone(obj, self.careables)

    def scoped_diff(self, old, new):
        return dict((a, (old.get(a), new.get(a))) for a in self.careables if old.get(a) != new.get(a))

    def _clone(self, obj, attrs):
        return dict((a, obj.get(a)) for a in attrs)

    def bulk_scoped_clone(self, objs):
        return [self.scoped_clone(o) for o in objs]


    def pushable_merge(self, target, source):
        diff = {}
        for attr in self.pushables:
            if target.get(attr) != source.get(attr):
                diff[attr] = (target.get(attr), source.get(attr))
                target[attr] = source.get(attr)
        return diff

    def pullable_merge(self, target, source):
        diff = {}
        for attr in self.pullables:
            if target.get(attr) != source.get(attr):
                diff[attr] = (target.get(attr), source.get(attr))
                target[attr] = source.get(attr)
        return diff


    def _get_hash(self):
        return self.get_hash(self.key)
    hash_ = property(_get_hash)

    def _get_pushables(self):
        return self.pushed + self.shared
    pushables = property(_get_pushables)

    def _get_pullables(self):
        return self.pulled + self.shared
    pullables = property(_get_pullables)

    def _get_careables(self):
        return self.pushed + self.pulled + self.shared
    careables = property(_get_careables)
