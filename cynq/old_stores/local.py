import base

# override this class, specify the class attributes, and implement the crud methods
class Local(base.Base):
    communal_attributes = []
    owned_attributes = []

    def __init__(self):
        super(Local, self).__init__()

    def all_(self):
        raise NotImplementedError()

    def update(self, obj):
        raise NotImplementedError()

    def create(self, obj):
        raise NotImplementedError()

    def before_sync_start(self):
        raise NotImplementedError()
    
    def after_sync_finish(self):
        raise NotImplementedError()

