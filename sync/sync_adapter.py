class CacheStore(BaseStore):
    def __init__(self, store):
        super(StoreCache,self).__init__()
        self.store = store

    def list_(self):
        if getattr(self,'list_cache', None) == None:
            self.list_cache = self.store.list_()
        return self.list_cache

    def update(self, obj):
        return self.store.update(obj)

    def create(self, obj):
        return self.store.create(obj)

    def delete(self, obj):
        return self.store.delete(obj)

    #TODO: figure out how to sync a single object instead of a list -- this method is just conjecture for now
    def get(self, id_):
        if getattr(self, 'list_cache', None) == None:
            self.list_cache = [self.store.get(id_)]

    def __iter__(self):
        return iter(self.list_())

    @property
    def key_name:
        self.store.key_name

    def 

class FacetedCacheStore(BaseStore):
    def __init__(self, store, key_name=None):
        super(StoreFacetCache,self).__init__()
        self.store = store
        key_name = key_name or self.store.key_name
        self.hash_cache = dict((getattr(o,key_name),o) for o in self.store if getattr(o,key_name,None))

    def __getitem__(self, key):
        self.hash_cache[key]

    def list_(self):
        self.hash_cache

    def update(self, obj):
        return self.store.update(obj)

    def create(self, obj):
        return self.store.create(obj)

    def delete(self, obj):
        return self.store.delete(obj)

class FacetedStoreCache(object):
    def __init__(self, store, key_names=None):
        super(StoreCache,self).__init__()
        self.store = store
        self.key_names = key_names or [self.store.key_name]
        self.list_cache = self.store.list_()
        for key_name in key_names:
            self.hash_cache[key_name] = dict((getattr(o,key_name),o) for o in self.list_cache if getattr(o,key_name,None))

    def 
    def _list


class SyncFacet(BaseStore):
    def __init__(self, store, key_name=None):
        super(SyncFacet,self).__init__()
        self.store = store
        self.key_name = key_name or self.store.key_name
        self.list_cache = self.store.list_()
        self.hash_cache = dict((getattr(o,self.key_name),o) for o in self.list_cache)
        
    def __getitem__(self, key):
        self.hash_cache[key]

class SyncConnection(object):
    def __init__(self, local_facet, remote_facet):
        super(SyncConnection,self).__init__()
        self.store = store
        self.list_cache = self.store.list_()
        self.hash_cache = dict((getattr(o,self.store.key),o) for o in self.list_cache)
 

