class BaseStore():
    def __init__(self):
        super(BaseStore, self).__init__()

    def pre_cynq(self, sync_started_at):
        self.stats = StoreStats(sync_started_at)

    def post_cynq(self):
        pass


class StoreStats():
    def __init__(self, key_attribute):
        self.creates = []
        self.updates = []
        self.deletes = []
        self.key_attribute = key_attribute

    def record_create(self, obj):
        self.creates.append(obj.get(self.key_attribute))

    def record_update(self, obj):
        self.updates.append(obj.get(self.key_attribute))

    def record_delete(self, obj):
        self.deletes.append(obj.get(self.key_attribute))

