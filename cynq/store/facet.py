from . import BaseStore

class FacetStore(BaseStore):
    # all the methods available to override (but should not be called directly by you ever!)
    def _all(self): return self.proxy_store.list_
    
    # you can choose to implement just the bulk ones or just the single ones-- not really a need to implement both
    def _bulk_create(self, dobjs): return self.proxy_store._bulk_create(dobjs)
    def _bulk_update(self, update_tuples): return self.proxy_store._bulk_update(update_tuples)
    def _bulk_delete(self, objs): return self.proxy_store._bulk_delete(objs)

    def _single_create(self, dobj): return self.proxy_store._single_create(dobj)
    def _single_update(self, obj, dchanges): return self.proxy_store._single_update(obj, dchanges)
    def _single_delete(self, obj): return self.proxy_store._single_delete(obj)

    def _pre_cynq(self): return self.proxy_store._pre_cynq()
    def _post_cynq(self): return self.proxy_store._post_cynq()

    def _createable(self): return self.proxy_store._createable()
    def _updateable(self): return self.proxy_store._updateable()
    def _deleteable(self): return self.proxy_store._deleteable()

    def __init__(self, proxy_store):
        super(FacetStore, self).__init__()
        self.proxy_store = proxy_store

