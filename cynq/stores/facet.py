from proxy import Proxy

class Facet(Proxy):
    def __init__(self, store, key_attribute):
        super(Facet, self).__init__(store)
        self.key_attribute = key_attribute
        self.cache = None

    def all_(self):
        return self.dict_().values()

    def create(self, obj):
        obj = super(Facet,self).create(obj)
        self._key_created_if_not_exists(obj)
        return obj

    def delete(self, obj):
        obj = super(Facet,self).delete(obj)
        self._key_deleted_if_exists(obj)
        return obj

    def dict_(self):
        if self.cache is None:
            _all = self.store.all_()
            self.cache = dict((getattr(o,self.key_attribute),o) for o in _all if getattr(o,self.key_attribute,None))
            self.leftovers = dict((id(o),o) for o in _all if not getattr(o,self.key_attribute,None) or id(o) not in (id(q) for q in self.cache.values()))
        return self.cache

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


# these two are also used by a MultiFacet if so hooked up

    def _key_created_if_not_exists(self, obj):
        key_value = getattr(obj, self.key_attribute, None)
        if key_value:
            current_obj = self[key_value]
            if current_obj and id(obj) != id(current_obj):
                self.leftovers[id(current_obj)] = current_obj
            self.dict_()[key_value] = obj
        else:
            self.leftovers[id(obj)] = obj

    def _key_deleted_if_exists(self, obj):
        key = getattr(obj, self.key_attribute, None)
        if key and key in self.dict_():
            del self.dict_()[key]
        elif id(obj) in self.leftovers:
            del self.leftovers[id(obj)]

