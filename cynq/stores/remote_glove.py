import proxy

class RemoteGlove(proxy.Proxy):

    def __init__(self, remote_store):
        super(RemoteGlove, self).__init__(remote_store)
        self.store = remote_store

    def list_(self):
        lst = self.store.list_()
        for obj in lst:
            setattr(obj, self.store.remote_expectation_attribute, True)
        return lst

    def create(self, obj):
        obj = self.store.create(obj)
        if obj:
            setattr(obj, self.remote_expectation_attribute, True)
        return obj

    def update(self, obj):
        obj = self.store.update(obj)
        if obj:
            setattr(obj, self.remote_expectation_attribute, True)
        return obj

    def update(self, obj):
        obj = self.store.update(obj)
        if obj:
            setattr(obj, self.remote_expectation_attribute, True)
        return obj

