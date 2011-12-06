from cynq.error import Error
import hashlib

class ChangeSet(object):
    def __init__(self, spec, creates=None, updates=None, deletes=None, keyless_creates=None):
        super(ChangeSet,self).__init__()
        self.spec = spec
        self.key = spec.key
        self.attrs = spec.attrs_with_key
        self.creates = creates or {}
        self.updates = updates or {}
        self.deletes = deletes or set()
        self.keyless_creates = keyless_creates or {}

    def __len__(self):
        return sum(len(getattr(self,a)) for a in ['creates','updates','deletes','keyless_creates'])

    #def copy(self):
        #kwargs = {'spec':set(self.spec) }
        #for a in ('creates','updates','deletes','keyless_creates'):
            #kwargs[a] = deepcopy(getattr(self,a))
        #return ChangeSet(**kwargs)

    def build(self, from_store, to_store, suppress_attrs=None):
        from_keys = set(from_store.hash_)
        to_keys = set(to_store.hash_)
        caring_attrs = set(self.attrs) - set(suppress_attrs or [])
        keyless_objects = set(from_store.list_) - set(from_store.hash_.values())
        self.keyless_creates = dict((self._hash(l),l) for l in [from_store.dscoped(o, caring_attrs, True) for o in keyless_objects])
        self.creates = dict((k,from_store.dscoped(from_store.hash_[k], caring_attrs)) for k in (from_keys - to_keys))
        self.updates = dict(kv for kv in ((k,from_store.ddiff(k,caring_attrs, to_store)) for k in (from_keys & to_keys)) if kv[1])
        self.deletes = set(to_keys - from_keys)

        # sanity checks:
        if set(self.creates) & set(self.updates) & self.deletes: raise Error("This should never happen!")

        return self

    def _ddiff(self, from_, to_):  # only diffs against keys present in from!
        return dict((a,from_.get(a)) for a in from_ if from_.get(a) != to_.get(a))

    def _hash(self, obj):
        return hashlib.sha256('|'.join([str(getattr(obj,attr,None)) for attr in self.attrs if attr != self.key])).hexdigest

    def subtract(self, changeset):
        # sanity checks:
        if set(self.creates) & set(changeset.updates): raise Error("This should never happen!")
        if set(self.creates) & changeset.deletes: raise Error("This should never happen!")
        if set(self.updates) & set(changeset.creates): raise Error("This should never happen!")
        if self.deletes & set(changeset.creates): raise Error("This should never happen!")

        # honor deletes over updates:
        for k in set(self.updates) & changeset.deletes: del self.updates[k]

        # remove duplicate measures
        for k in self.deletes & changeset.deletes: self.deletes.remove(k)
        for k in set(self.creates) & set(changeset.creates): 
            create_obj = self.creates.pop(k)
            diff = self._ddiff(create_obj, changeset.creates[k])
            if diff: self.updates[k] = diff

        # update keys on similar looking keyless creates (this situation could only occur after certain cynq failures (or creation of like objects on both sides within cynq cycle)
        creates_by_hash = dict((self._hash(o),o) for o in changeset.creates.values())
        for h in set(self.keyless_creates) & set(creates_by_hash):
            dobj, keyless_trigger = self.keyless_creates[h]
            keyless_trigger(getattr(creates_by_hash[h], self.key))
            del self.keyless_creates[h]  # no longer needed now

        # change updates or remove if complete duplicate
        for k in set(self.updates) & set(changeset.updates):
            for attr in self.attrs:
                if self.updates[k].has_key(attr) and changeset.updates[k].has_key(attr):
                    if self.updates[k][attr]==changeset.updates[k][attr]:
                        del self.updates[k][attr]
#                    else 
            if not self.updates[k]: 
                del self.updates[k] # remove if nothing left to change

        # sanity checks:
        if set(self.creates) & set(self.updates) & self.deletes: raise Error("This should never happen!")
        return self


