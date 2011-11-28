from copy import deepcopy

class ChangeSet(object):
    def __init__(self, attrs, key, creates=None, updates=None, deletes=None, orphaned_creates=None):
        super(ChangeSet,self).__init__()
        self.attrs = tuple(attrs)
        self.key = key
        self.creates = creates or {}
        self.updates = updates or {}
        self.deletes = deletes or {}
        self.orphaned_creates = orphaned_creates or {}

    def copy(self):
        kwargs = {'attrs':self.attrs, 'key':self.key}
        for a in ('creates','updates','deletes','orphaned_creates'):
            kwargs[a] = deepcopy(getattr(self,a))
        return ChangeSet(**kwargs)

    def build(self, fresh_list, snapshot_list):
        fresh_hash = dict((o[self.key],o) for o in fresh_list if o.get(self.key) is not None)
        snapshot_hash = dict((o[self.key],o) for o in snapshot_list if o.get(self.key) is not None)
        fresh_keys = set(fresh_hash)
        snapshot_keys = set(snapshot_hash)
        self.orphaned_creates = dict((id(o),self._scope(o)) for o in fresh_list if o.get(self.key) is None)
        self.creates = dict((k,self._scope(fresh_hash[k])) for k in (fresh_keys - snapshot_keys))
        self.updates = dict(kv for kv in ((k,self._diff(fresh_hash[k],snapshot_hash[k])) for k in (fresh_keys & snapshot_keys)) if kv[1])
        self.deletes = dict((k,self._scope(snapshot_hash[k])) for k in (snapshot_keys - fresh_keys))

        # sanity checks:
        if set(self.creates) & set(self.updates) & set(self.deletes): raise Error("This should never happen!")

        return self

    def _diff(self, fresh, stale):
        return dict((a,getattr(fresh,a,None)) for a in self.attrs if getattr(fresh,a,None) != getattr(stale,a,None))

    def _scope(self, obj):
        return dict((attr,getattr(obj,attr,None)) for attr in self.attrs) 

    def merge(self, changeset):
        # sanity checks:
        if set(self.creates) & set(changeset.updates): raise Error("This should never happen!")
        if set(self.creates) & set(changeset.deletes): raise Error("This should never happen!")
        if set(self.updates) & set(changeset.creates): raise Error("This should never happen!")
        if set(self.deletes) & set(changeset.creates): raise Error("This should never happen!")

        # overrides:
        for k in set(self.deletes) & set(changeset.updates): del self.deletes[k]
        for k in set(self.updates) & set(changeset.deletes): del self.updates[k]

        # update creates and deletes
        self.orphaned_creates.update(changeset.orphaned_creates)
        self.creates.update(changeset.creates)
        self.deletes.update(changeset.deletes)

        # update updates that aren't shared
        overlap = set(self.updates) & set(changeset.updates)
        self.updates.update(dict((k,v) for k,v in changeset.updates.iteritems() if k not in overlap))

        # for updates that are shared, we can go down to attribute levels
        for k in overlap_update_keys:
            for attr in self.attrs:
                if changeset.updates[k].has(attr):
                    self.updates[k][attr] = changeset.updates[k][attr]
            self.updates[k]
        self.updates.update(changeset.updates)

        # sanity checks:
        if set(self.creates) & set(self.updates) & set(self.deletes): raise Error("This should never happen!")
        return self

    def _filter_(self, list_):
        leftovers = dict((id(o),self._scope(o)) for o in list_ if o.get(self.key) is None)
        hash_ = dict((o[self.key],self._scope(o)) for o in list_ if o.get(self.key) is not None)
        for k in set(self.deletes):
            if k not in hash_: del self.deletes[k]
        for k in set(self.creates):
            if k in hash_: self.updates[k] = self.creates.pop(k)
        for k in set(self.updates):
            if k not in hash_: raise Error("This should never happen!")
            for a,v in hash_[k].iteritems():
                if self.updates[k].has(a) and self.updates[k][a] == v:
                    del self.updates[k][a]
        self.updates = dict((k,v) for k,v in self.updates.iteritems() if v)
        return self

    def _apply(self, store):
        creates = dict((o.get(self.key),o) for o in store.create(deepcopy(self.creates)))
        updates = dict((o.get(self.key),o) for o in store.update(deepcopy(self.updates)))
        deletes = dict((o.get(self.key),o) for o in store.delete(deepcopy(self.deletes)))
        if self.orphaned_creates:
            creates.update(dict((o.get(self.key),o) for o in store.create(deepcopy(self.orphaned_creates))))
        return ChangeSet(self.attrs, self.key, creates, updates, deletes)

    def apply_subtracting_errors(self, store):
        hash_ = dict((o[self.key],self._scope(o)) for o in store.list_ if o.get(self.key) is not None)
        deletes = [self.deletes[k] for k in self.deletes if k not in hash_]
        (successes, failures, leftovers) = store.delete(deletes)
        for removal in failures + leftovers:
            self.deletes[removal]
            HERHEHERHEHEHREHHERHRE

        for k in set(self.deletes):
            if k not in hash_: del self.deletes[k]
        deletes = dict((o.get(self.key),o) for o in store.delete(deepcopy(self.deletes)))



    def filter_and_apply(self, store):
        self.filter_(store.list_)
        return self.apply(store)


class Store(object):
    def __init__(self):
        super(Store,self).__init__()

    def all_(self):
        pass

    def create(self, create_set):


    def apply_changeset(self, changeset):
        self.


class DjangoCacheStore(object):
    def __init__(self):
        super(Store,self).__init__()

    def all_(self):
        pass

    def create(self, create_set):


        


class Controller(object):
    def __init__(self, local, remotes):
        super(Controller,self).__init__()
        self.local = local
        self.remotes = remotes

    def cynq(self):
        started_at = sanetime()

    def _pre_cynq(self, started_at):
        if not self.local.spec.pre_cynq(started_at):
            self.log.warn("pre-cynq hook on local store prevented cynq execution %s" % self.local_store)
            return False
        remote_stores_to_sync = []
        for rs in self.remote_stores:
            if rs.spec.pre_cynq(cynq_started_at):
                remote_stores_to_sync.append(rs)
            else:
                self.log.warn("pre-cynq hook on remote store prevented it from being included in cynq (rs:%s)" % rs)
        if not remote_stores_to_sync:
            self.log.warn("all remote stores were excluded by pre-cynq hooks, so no cynq happening")
            return False
        return remote_stores_to_sync

    




