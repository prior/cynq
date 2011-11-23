FIELD_PROXIES = ['id_', 'createable', 'updateable', 'deleteable', 'pushed', 'pulled', 'shared', 'key', 'since']


class RemoteStore(BaseStore):
    def __init__(self, remote_spec):
        super(RemoteStore,self).__init__(self, remote_spec)  #_TODO: ensure that spec passed is a remote spec
        self._build_spec_proxies()
        self._hash = None

    def caring

    def supplement_since(self, local_list):
        since_attr = self.spec.since
        

        self.since_value = 

            self.rs.supplement_since(self.ls.list_)

    def _build_spec_proxies(self):
        for field in FIELD_PROXIES:
            setattr(self, field) = getattr(self.spec, field)

    
    def _get_id(self):



    createable = True
    updateable = True
    deleteable = True

    # attributes
    pushed = ()
    pulled = ()
    shared = ()
    key = None
    since = None

        ['pulled','pushed','shared','key',
        self.pulled = self.spec.__class__.pulled



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


    def writeablely_clone(self, obj):
        return dict((attr, obj.get(attr)) for attr in (self.writeables))

    def is_writeably_different(self, obj):
        return any((for attr in 

    def _get_writeables(self):
        return self.shared + self.pulled
    writeables = property(_get_writeables)

