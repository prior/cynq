from . import BaseStore

class BaseMemoryStore(BaseStore):
    def __init__(self, item_kls, items_payload=None):
        super(BaseMemoryStore, self).__init__()
        self.item_kls = item_kls
        self.items = items_payload or {}

    def _all(self): 
        return self.items.values()
    
    def _single_create(self, dobj):
        item = self.item_kls(**dobj)
        self.items[id(item)] = item
        return item

    def _single_update(self, item, dchanges):
        for k,v in dchanges.iteritems():
            setattr(item, k, v)
        return item

    def _single_delete(self, item):
        del self.items[id(item)]
        return item

