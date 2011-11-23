
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

    def _get_total_changes(self):
        return sum(getattr(self,stat) for stat in ['creates','updates','deletes'])
    total_changes = property(_get_total_changes)

    

