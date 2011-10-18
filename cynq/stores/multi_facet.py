from stores.read_cache import ReadCache
from stores.facet import Facet

# only really makes sense on a local store (at least right now), cuz it depends on ReadCache which requires object be identified by id -- so no copying/cloning allowed -- which happens to work for the local side right now
class MultiFacet(ReadCache):
    def __init__(self, store):
        super(MultiFacet, self).__init__(store)
        self.facets = {} 

    def get_facet(self, key_attribute):
        facet = self.facets.get(key_attribute, None)
        if not facet:
            facet = self.facets[key_attribute] = Facet(self, key_attribute)
        return facet

    def create(self, obj):
        obj = super(MultiFacet, self).create(obj)
        for facet in self.facets.values():
            facet.key_created_if_not_exists(obj)
        return obj

    def update(self, obj):
        obj = super(MultiFacet, self).update(obj)
        for facet in self.facets.values():
            facet.key_created_if_not_exists(obj)
        return obj

    def delete(self, obj):
        obj = super(MultiFacet, self).delete(obj)
        for facet in self.facets.values():
            facet.key_deleted_if_exists(obj)
        return obj

