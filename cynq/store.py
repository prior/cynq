#_TODO: figure out implications of an update of a key attribute-- should we be disallowing such an action

class BaseStore(object):
    def __init__(self, spec):
        super(BaseStore, self).__init__()
        self.spec = spec
        self._list = None
        self._queued = {'creates':[], 'updates':[], 'deletes':[]}

    def _force_get_list(self):
        return self.spec._all()

    def _get_list(self):
        if self._list is None:
            self._list = self.self._force_get_list()
        return self._list
    list_ = property(_get_list)

    def _force_build_hash(self, key_attr):
        return dict((o[key_attr],o) for o in self.list_ if o.get(key_attr) is not None)

    # playing with objects in that exist in the _list
    def create(self, objs, persist=False): return self.change(objs, 'create', persist)
    def update(self, objs, persist=False): return self.change(objs, 'update', persist)
    def delete(self, objs, persist=False): return self.change(objs, 'delete', persist)
    def change(self, objs, change_type, persist=False):
        self._queued['%ss'%change_type].append(objs)
        getattr(self,'_%sd'%change_type)(objs)
        if persist: self.persist_changes()

    def persist_changes(self):
        for change_type in ['create','update','delete']:
            queue = self._queued['%ss'%change_type]
            if queue:
                getattr(self.spec,'_batch_%s'%change_type)(queue)


    def _created(self, objs): self.list_.extend(objs)
    def _updated(self, objs): pass
    def _deleted(self, objs): [self.list_.remove(o) for o in objs]






class LocalStore(BaseStore):
    def __init__(self, spec):
        self._hashes = {}
        
    def get_hash(self, key_attr):
        if self._hashes.get(key_attr) is None:
            self._hashes[key_attr] = self.force_build_hash(key_attr)
        return self._hashes[key_attr]

    # playing with objects in that exist in the _list
    def _created(self, objs):
        super(BaseStore,self)._created(self, objs)
        for key in self._hashes:
            for obj in objs:
                key_value = obj.get(key)
                if key_value is not None:
                    if key_value in self.hash_: raise Error("key already exists!")  #_TODO: embellish
                    if obj in self.values(): raise Error("obj already in hash!")  #_TODO: embellish
                    self._hashes[key][key_value] = obj

    def _updated(self, obj):
        super(BaseStore,self)._updated(self, objs)
        for key in self._hashes:
            for obj in objs:
                key_value = obj.get(key)
                if key_value is not None:
                    if key_value in self.hash_ and self.hash_[key_value] != obj: 
                        raise Error("object should be the same!")  #_TODO: embellish
                    if key_value in s
                else:
                    if obj in self.values(): raise Error("obj already in hash!")  #_TODO: embellish
                    self._hashes[


            key_value = obj.get(self.spec.key)
            if key_value is None: raise Error("this needs to have a key")  #_TODO: embellish
            if key_value not in self.hash_: raise Error("key should already exist!")  #_TODO: embellish
            if self.hash_[key_value] != obj: raise Error("object should be the same!")  #_TODO: embellish

    def _deleted(self, obj): self.list_.remove(obj)
        super(RemoteStore,self)._deleted(self, objs)
        for obj in objs:
            key_value = obj.get(self.spec.key)
            if key_value is None: raise Error("this needs to have a key")  #_TODO: embellish
            if key_value not in self.hash_: raise Error("key should already exist!")  #_TODO: embellish
            del self.hash_[key_value]


            if self.remote_spec.since and self.remote_spec.sinceable and self.local_objects: 
                since = max(lo[self.remote_spec.since] for lo in self.local_objects)
                self._remote_objects = dict(
                    (self.
               self.max_since(self.remote_speclocal_objects = 

            else:

        return self._remote_objects
    objects = property(_get_objects)


class RemoteStore(BaseStore):
    def __init__(self, spec):
        super(RemoteStore,self).__init__(self, spec)  #_TODO: ensure that spec passed is a remote spec
        self._hash = None

    def _get_hash(self):
        if self._hash is None:
            self._hash = self._force_build_hash(self.spec.key)
        return self._hash
    hash_ = property(_get_hash)

    def _force_get_list(self):
        if self.spec.sinceable and self.spec.since and self.local_objects: 
            since = max(lo[self.spec.since] for lo in self.local_objects)
            list
            self.spec.all_(since = since)
            objects = dict((self.speck.key for lo in self.
                    (self.
               self.max_since(self.remote_speclocal_objects = 

        

    def _created(self, objs):
        super(RemoteStore,self)._created(self, objs)
        for obj in objs:
            for key in self._hashes:
                key_value = obj.get(key)
                self._hash_[key_value] = obj
                if key_value is None: raise Error("this needs to have a key")  #_TODO: embellish
                if key_value in self.hash_: raise Error("key already exists!")  #_TODO: embellish
                self.hash_[key_value] = obj

    def _updated(self, obj): pass
        super(RemoteStore,self)._updated(self, objs)
        for obj in objs:
            key_value = obj.get(self.spec.key)
            if key_value is None: raise Error("this needs to have a key")  #_TODO: embellish
            if key_value not in self.hash_: raise Error("key should already exist!")  #_TODO: embellish
            if self.hash_[key_value] != obj: raise Error("object should be the same!")  #_TODO: embellish

    def _deleted(self, obj): self.list_.remove(obj)
        super(RemoteStore,self)._deleted(self, objs)
        for obj in objs:
            key_value = obj.get(self.spec.key)
            if key_value is None: raise Error("this needs to have a key")  #_TODO: embellish
            if key_value not in self.hash_: raise Error("key should already exist!")  #_TODO: embellish
            del self.hash_[key_value]


    def writablely_clone(self, obj):
        return dict((attr, obj.get(attr)) for attr in (self.spec.shared + self.spec.pulled))

    def is_writeably_different(self, obj):
        return any((for attr in 

