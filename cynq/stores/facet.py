from stores.keyed_read_cache import KeyedReadCache

# easy exposure across a given key
class Facet(KeyedReadCache):
    def __init__(self, store, key_attribute):
        super(Facet,self).__init__(store, key_attribute)

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
        self.dict_()[getattr(obj, self.key_attribute)] = obj

    def _key_deleted_if_exists(self, obj):
        key = getattr(obj, self.key_attribute)
        if key in self.dict_():
            del self.dict_()[key]





