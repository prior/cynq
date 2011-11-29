from copy import deepcopy

class ChangeSet(object):
    def __init__(self, spec, creates=None, updates=None, deletes=None, keyless_creates=None):
        super(ChangeSet,self).__init__()
        self.spec = spec
        self.key = spec.key
        self.attrs = spec.attrs_with_key
        self.creates = creates or {}
        self.updates = updates or {}
        self.deletes = deletes or {}
        self.keyless_creates = keyless_creates or {}

    def __len__(self):
        return sum(len(getattr(self,a)) for a in ['creates','updates','deletes','keyless_creates'])

    def copy(self):
        kwargs = {'spec':set(self.spec) }
        for a in ('creates','updates','deletes','orphaned_creates'):
            kwargs[a] = deepcopy(getattr(self,a))
        return ChangeSet(**kwargs)

    def build(self, from_store, to_store):
        from_keys = set(from_store.hash_)
        to_keys = set(to_store_.hash_)
        self.keyless_creates = dict((self._hash(l),l) for l in [self._scope(o,from_store) for o in from_store.list_ if o.get(self.key) is None])
        self.creates = dict((k,self._scope(from_store.hash_[k])) for k in (from_keys - to_keys))
        self.updates = dict(kv for kv in ((k,(self._diff(from_store.hash_[k],to_store.hash_[k]),from_store.hash_[k],to_store.hash[k])) for k in (from_keys & to_keys)) if kv[1])
        self.deletes = dict((k,self._scope(to_store.hash_[k])) for k in (to_keys - from_keys))

        # sanity checks:
        if set(self.creates) & set(self.updates) & set(self.deletes): raise Error("This should never happen!")

        return self

    def _diff(self, from_, to_):
        return dict((a,getattr(from_,a,None)) for a in self.attrs if getattr(from_,a,None) != getattr(to_,a,None))

    def _scope(self, obj, keyless_trigger_store=False):
        d = dict((attr,getattr(obj,attr,None)) for attr in self.attrs) 
        if add_keyless_trigger:
            d['_keyless_trigger_store'] = keyless_trigger_store
            d['_keyless_trigger_object'] = obj
        return d

    def _hash(self, obj):
        return hashlib.sha256('|'.join([str(getattr(obj,attr,None)) for attr in self.attrs if attr != self.key])).hexdigest

    def subtract(self, changeset):
        # sanity checks:
        if set(self.creates) & set(changeset.updates): raise Error("This should never happen!")
        if set(self.creates) & set(changeset.deletes): raise Error("This should never happen!")
        if set(self.updates) & set(changeset.creates): raise Error("This should never happen!")
        if set(self.deletes) & set(changeset.creates): raise Error("This should never happen!")

        # honor deletes over updates:
        for k in set(self.updates) & set(changeset.deletes): del self.updates[k]

        # remove duplicate measures
        for k in set(self.deletes) & set(changeset.deletes): del self.deletes[k]
        for k in set(self.creates) & set(changeset.creates): 
            create_obj = self.creates.pop(k)
            diff = self._diff(create_obj, changeset.creates[k])
            if diff: self.updates[k] = (diff, create_obj, changeset.creates[k])

        # remove similar looking keyless creates
        creates_by_hash = dict((self._hash(o),o) for o in changeset.creates.values())
        for h in set(self.keyless_creates) & set(creates_by_hash): del self.keyless_creates[h]

        # change updates or remove if complete duplicate
        for k in set(self.updates) & set(changeset.updates):
            for attr in self.attrs:
                if self.updates[k][0].has(attr) and changeset.updates[k][0].has(attr) and self.updates[k][0][attr]==changeset.updates[k][0][attr]:
                    del self.updates[k][0][attr]
            if not self.updates[k][0]: del self.updates[k] # remove if nothing left to change

        # sanity checks:
        if set(self.creates) & set(self.updates) & set(self.deletes): raise Error("This should never happen!")
        return self

    #def mold(self, store):
        #leftovers = dict((id(o),self._scope(o)) for o in list_ if o.get(self.key) is None)

        ## let incoming deletes take priority (delete seems like a command we should respect more than update even if it's coming from remote
        #for k in set(self.deletes) - set(store.hash_): del self.deletes[k]
        #for k in set(self.updates) - set(store.hash_): del self.updates[k]

        ## drop creates down to updates or nothing at all depending
        #for k in set(self.creates) & set(store.hash_):
            #create_obj = self.creates.pop(k)
            #diff = self._diff(create_obj, store.hash_[k])
            #if diff: self.updates[k] = (diff, create_obj, store.hash_[k])

        ## remove similar looking keyless creates
        #existing_by_hash = dict((self._hash(o),o) for o in changeset.creates.values())
        #for h in set(self.keyless_creates) & set(creates_by_hash): del self.keyless_creates[h]
        

            #c

            #if k not in store.hash_: del self.deletes[k]
        #for k in list(self.creates):
            #if k in hash_: self.updates[k] = self.creates.pop(k)
        #for k in set(self.updates):
            #if k not in hash_: raise Error("This should never happen!")
            #for a,v in hash_[k].iteritems():
                #if self.updates[k].has(a) and self.updates[k][a] == v:
                    #del self.updates[k][a]
        #self.updates = dict((k,v) for k,v in self.updates.iteritems() if v)
        #return self

    
    #def merge(self, changeset):
        ## sanity checks:
        #if set(self.creates) & set(changeset.updates): raise Error("This should never happen!")
        #if set(self.creates) & set(changeset.deletes): raise Error("This should never happen!")
        #if set(self.updates) & set(changeset.creates): raise Error("This should never happen!")
        #if set(self.deletes) & set(changeset.creates): raise Error("This should never happen!")

        ## overrides:
        #for k in set(self.deletes) & set(changeset.updates): del self.deletes[k]
        #for k in set(self.updates) & set(changeset.deletes): del self.updates[k]

        ## update creates and deletes
        #self.orphaned_creates.update(changeset.orphaned_creates)
        #self.creates.update(changeset.creates)
        #self.deletes.update(changeset.deletes)

        ## update updates that aren't shared
        #overlap = set(self.updates) & set(changeset.updates)
        #self.updates.update(dict((k,v) for k,v in changeset.updates.iteritems() if k not in overlap))

        ## for updates that are shared, we can go down to attribute levels
        #for k in overlap_update_keys:
            #for attr in self.attrs:
                #if changeset.updates[k].has(attr):
                    #self.updates[k][attr] = changeset.updates[k][attr]
            #self.updates[k]
        #self.updates.update(changeset.updates)

        ## sanity checks:
        #if set(self.creates) & set(self.updates) & set(self.deletes): raise Error("This should never happen!")
        #return self

    #def apply_(self, store):
        #rcreates = store.create(self.creates)[1]
        #rupdates = store.update(self.updates)[1]
        #rdeletes = store.delete(self.deletes)[1]
        #rorphans = ([],[])
        #if self.orphaned_creates:
            #rorphans = store.create(self.orphaned_creates)
        #return (rcreates[0]+rupdates[0]+rdeletes[0]+rorphans[0], rcreates[1]+rupdates[1]+rdeletes[1]+rorphans[1]) 

    #def remove_changed

        
        #updates = dict((o.get(self.key),o) for o in store.update(deepcopy(self.updates)))
        #deletes = dict((o.get(self.key),o) for o in store.delete(deepcopy(self.deletes)))
        #return ChangeSet(self.attrs, self.key, creates, updates, deletes)

    #def apply_subtracting_errors(self, store):
        #hash_ = dict((o[self.key],self._scope(o)) for o in store.list_ if o.get(self.key) is not None)
        #deletes = [self.deletes[k] for k in self.deletes if k not in hash_]
        #(successes, failures, leftovers) = store.delete(deletes)
        #for removal in failures + leftovers:
            #self.deletes[removal]
            #HERHEHERHEHEHREHHERHRE

        #for k in set(self.deletes):
            #if k not in hash_: del self.deletes[k]
        #deletes = dict((o.get(self.key),o) for o in store.delete(deepcopy(self.deletes)))



    #def filter_and_apply(self, store):
        #self.filter_(store.list_)
        #return self.apply(store)


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

    




