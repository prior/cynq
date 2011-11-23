from cynq.stores.local import Local

# override this class, specify the class attributes, and implement the crud methods
class DjangoLocal(Local):
    communal_attributes = []
    owned_attributes = []
    key_attribute = None


    def __init__(self):
        super(DjangoLocal, self).__init__()

    def list_(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()

    def update(self, obj):
        obj.save()
        return obj

    def create(self, obj):
        obj.save()
        return obj

    def before_sync_start(self):
        raise NotImplementedError()
    
    def after_sync_finish(self):
        raise NotImplementedError()



