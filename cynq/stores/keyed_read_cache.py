from proxy import Proxy

class KeyedReadCache(Proxy):
    def __init__(self, store, key_attribute):
        super(KeyedReadCache, self).__init__(store)
        self.key_attribute = key_attribute
        self.cache = None

    def list_(self):
        return self.dict_().values()

    def dict_(self):
        if self.cache is None:
            self.cache = dict((getattr(o,self.key_attribute),o) for o in self.store.list_() if getattr(o,self.key_attribute,None))
        return self.cache

    def create(self, obj):
        obj = super(KeyedReadCache, self).create(obj)
        if getattr(obj, self.key_attribute, None):
            self.dict_()[getattr(obj, self.key_attribute)] = obj
        return obj

    def update(self, obj):
        obj = super(KeyedReadCache, self).update(obj)
        if getattr(obj, self.key_attribute, None):
            self.dict_()[getattr(obj, self.key_attribute)] = obj
        return obj

    def delete(self, obj):
        obj = super(KeyedReadCache, self).delete(obj)
        if getattr(obj, self.key_attribute, None):
            del self.dict_()[getattr(obj, self.key_attribute)]
        return obj

    def __iter__(self):
        return iter(self.dict_())

    def __contains__(self, key):
        return key in self.dict_()

    def __getitem__(self, key):
        return self.dict_().get(key, None)

    def __and__(self, other): # other must also be a Facet
        return set(self) & set(other)

    def __sub__(self, other): # other must also be a Facet
        return set(self) - set(other)


# these two are used only if hooked up to a MultiFacet

    def _key_created_if_not_exists(self, obj):
        if getattr(obj, self.key_attribute, None):
            self.dict_()[getattr(obj, self.key_attribute)] = obj

    def _key_deleted_if_exists(self, obj):
        key = getattr(obj, self.key_attribute, None)
        if key and key in self.dict_():
            del self.dict_()[key]

