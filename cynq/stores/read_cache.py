from proxy import Proxy

# NOTE: for this to work as expected, you need to make sure that the same objects get passed around through this class-- not copies of objects
# TODO: fix documentation
class ReadCache(Proxy):
    def __init__(self, store):
        super(ReadCache, self).__init__(store)
        self.cache = None

    def all_(self):
        if self.cache is None:
            self.cache = set(self.store.all_())
        return self.cache

    def create(self, obj):
        obj = super(ReadCache, self).create(obj)
        self.cache.add(obj)
        return obj

    def delete(self, obj):
        obj = super(ReadCache, self).delete(obj)
        self.cache.remove(obj)
        return obj

