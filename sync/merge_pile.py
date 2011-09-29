class MergePile(object):
    def __init__(self, list_, keys):
        self.list_ = list(list_)
        self.keys = list(keys)
        self.pointers = {}
        for k in keys:
            self.pointers[k] = {}
        for obj in self.list_:
            self._establish_pointers(obj)

    def get(self, key, id_):
        return self.pointers[key].get(id_)

    def add(self, obj):
        self.list_.append(obj)
        self._establish_pointers(obj)

    def missing_objects(self, key, ids):
        id_set = set(ids)
        return [o for o in self.list_ if getattr(o,key,None) not in id_set]

    def common_objects(self, key, ids):
        return [self.pointers[key][id_] for id_ in set(self.pointers[key]).intersection(ids)]

    def persist_changes(self, local_store):
        for obj in self.list_:
            if getattr(obj, '_updated', None):
                local_store.save(obj)

    def _establish_pointers(self, obj):
        for k in self.keys:
            id_ = getattr(obj, k, None)
            if id_:
                self.pointers[k][id_] = obj
