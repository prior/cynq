import base

class ProxyStore(base.BaseStore):
    def __init__(self, store):
        super(ProxyStore, self).__init__()
        self.store = store
        for attr in base.STORE_DESIGNATIONS:
            if getattr(store, attr, None):
                setattr(self, attr, getattr(store, attr))

    def list_(self):
        return self.store.list_()

    def create(self, obj):
        return self.store.create(obj)

    def update(self, obj):
        return self.store.update(obj)

    def delete(self, obj):
        return self.store.delete(obj)
    

