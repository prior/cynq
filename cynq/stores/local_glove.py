from read_cache import ReadCache

# assumes all objects going through here are always the same objects --no copy/clones -- relying on id to match things up
class LocalGlove(ReadCache):

    def __init__(self, local_store):
        super(LocalGlove, self).__init__(local_store)
        self.created = []

    def create(self, obj):
        # purposefully avoiding a call to super here -- don't want to change the initial list
        self.created.append(obj)
        return obj

    def update(self, obj):
        raise NotImplementedError("should not be hitting this")

    def delete(self, obj):
        raise NotImplementedError("should not be hitting this")

    # purposefully going through all objects and saving them one by one
    def persist(self, synced_at):
        for obj in self.all_():
            obj.syncable_updated_at = synced_at
            obj.synced_at = synced_at
            self.store.update(obj)

        for obj in self.created:
            obj.syncable_updated_at = synced_at
            obj.synced_at = synced_at
            self.store.create(obj)

