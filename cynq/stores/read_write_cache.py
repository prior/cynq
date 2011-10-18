from read_cache import ReadCache

class LocalGlove(ReadCache):
    def __init__(self, store):
        super(ReadWriteCache, self).__init__(store)
        changeset = set()

    def create(self, obj):
        changeset.add(obj)

    def update(self, obj):
        changeset.add(obj)

    def delete(self, obj):
        obj.deleted_at
        changeset.add(obj)

    def flush_

