from . import BaseStore

class FacetStore(BaseStore):
    #def _all(self):  # not needed in facet since we're purposefully proxying through (and proxying through the cache as well for the list anyway)

    def _bulk_create(self, dobjs): return self.proxy_store._bulk_create(dobjs)
    def _bulk_update(self, update_tuples): return self.proxy_store._bulk_update(update_tuples)
    def _bulk_delete(self, objs): return self.proxy_store._bulk_delete(objs)

    def _single_create(self, dobj): return self.proxy_store._single_create(dobj)
    def _single_update(self, obj, dchanges): return self.proxy_store._single_update(obj, dchanges)
    def _single_delete(self, obj): return self.proxy_store._single_delete(obj)

    def _pre_cynq(self): return self.proxy_store._pre_cynq()
    def _post_cynq(self): return self.proxy_store._post_cynq()

    def _createable(self, arm): return self.proxy_store._createable(arm)
    def _updateable(self, arm): return self.proxy_store._updateable(arm)
    def _deleteable(self, arm): return self.proxy_store._deleteable(arm)

    def __init__(self, proxy_store):
        super(FacetStore, self).__init__()
        self.proxy_store = proxy_store

    def _get_list(self):
        if self._list is None:
            self._list = self.proxy_store.list_
        return self._list
    list_ = property(_get_list)
