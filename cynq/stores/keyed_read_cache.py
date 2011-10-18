from proxy import Proxy

class KeyedReadCache(Proxy):
    def __init__(self, store, key_attribute):
        super(KeyedReadCache, self).__init__(store)
        self.key_attribute = key_attribute
        self.cache = None

    def list_(self):
        return self.dict_().values()

    def dict_(self):
        if self.cache is not None:
            self.cache = dict((o[getattr(o,self.key_attribute)],o) for o in self.store.list_() if getattr(o,self.key_attribute,None))
        return self.cache.values()

    def create(self, obj):
        obj = super(KeyedReadCache, self).create(obj)
        if getattr(obj, self.key_attribute, None):
            self.cache[getattr(obj, self.key_attribute)] = obj
        return obj

    def update(self, obj):
        obj = super(KeyedReadCache, self).update(obj)
        if getattr(obj, self.key_attribute, None):
            self.cache[getattr(obj, self.key_attribute)] = obj
        return obj

    def delete(self, obj):
        obj = super(KeyedReadCache, self).delete(obj)
        if getattr(obj, self.key_attribute, None):
            del self.cache[getattr(obj, self.key_attribute)]
        return obj

