from proxy import Proxy

class Facet(Proxy):
    def __init__(self, store, key_attribute):
        super(Facet, self).__init__(store)
        self.key_attribute = key_attribute
        self.cache = None

    def list_(self):
        return self.dict_().values()

    def create(self, obj):
        obj = super(Facet,self).create(obj)
        self._key_created_if_not_exists(obj)

    def update(self, obj):
        current_obj = getattr(obj,self.key_attribute)
        if getattr(self, 'communal_attributes', None) is not None:
            for attr in getattr(self,'communal_attributes'):
                if getattr(obj,attr) != getattr(current_obj,attr):
                    obj = super(Facet,self).update(obj)
                    break
        else:
            obj = super(Facet,self).update(obj)
        return obj

    def delete(self, obj):
        obj = super(Facet,self).delete(obj)
        self._key_deleted_if_exists(obj)

    def dict_(self):
        if self.cache is None:
            self.cache = dict((getattr(o,self.key_attribute),o) for o in self.store.list_() if getattr(o,self.key_attribute,None))
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


# these two are used only if hooked up to a MultiFacet

    def _key_created_if_not_exists(self, obj):
        if getattr(obj, self.key_attribute, None):
            self.dict_()[getattr(obj, self.key_attribute)] = obj

    def _key_deleted_if_exists(self, obj):
        key = getattr(obj, self.key_attribute, None)
        if key and key in self.dict_():
            del self.dict_()[key]

