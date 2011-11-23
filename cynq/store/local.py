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


