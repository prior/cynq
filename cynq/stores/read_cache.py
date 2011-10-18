from proxy import Proxy

# NOTE: for this to work as expected, you need to make sure that the same objects get passed around through this class-- not copies of objects
# TODO: fix documentation
class ReadCache(Proxy):
    def __init__(self, store, key_attribute=None):
        super(ReadCache, self).__init__(store)
        self.cache = None

    def list_(self):
        if self.cache is not None:
            self.cache = self.store.list_()
        return self.cache

    def create(self, obj):
        obj = super(ReadCache, self).create(obj)
        self.cache.append(obj)
        return obj

    def delete(self, obj):
        obj = super(ReadCache, self).delete(obj)
        self.cache.delete(obj)
        return obj

