from proxy import Proxy

# NOTE: for this to work as expected, you need to make sure that the same objects get passed around through this class-- not copies of objects
# TODO: fix documentation
class ReadCache(Proxy):
    def __init__(self, store):
        super(ReadCache, self).__init__(store)
        self.cache = None

    def all_(self):
        if self.cache is None:
            self.cache = list(self.store.all_())
        return self.cache

    def create(self, obj):
        obj = super(ReadCache, self).create(obj)
        self.cache.append(obj)
        return obj


    # is this even being used?  if it is then we're probably in trouble for Django Models that have id's of None
    #    a call to this would wipe all None id's -- i think
    #  I don't think it's being used though since ReadCache is only used by the local side which never does hard deletes-- i think
    def delete(self, obj):
        obj = super(ReadCache, self).delete(obj)
        self.cache.remove(obj)
        return obj

