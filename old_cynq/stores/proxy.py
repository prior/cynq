import base

class Proxy(base.Base):
    def __init__(self, store):
        super(Proxy, self).__init__()
        self.store = store
        for attr in base.STORE_DESIGNATIONS:
            if getattr(store, attr, None):
                setattr(self, attr, getattr(store, attr))

    def all_(self):
        return self.store.all_()

    def create(self, obj):
        return self.store.create(obj)

    def update(self, obj):
        return self.store.update(obj)

    def delete(self, obj):
        return self.store.delete(obj)

    def __unicode__(self):
        return 'Proxy(%s)' % self.store

    def __str__(self):
        return self.__unicode__()
    

