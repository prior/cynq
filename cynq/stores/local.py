import base

# override this class, specify the class attributes, and implement the crud methods
class Local(base.Base):
    communal_attributes = []
    owned_attributes = []
    key_attribute = None

    def __init__(self, store):
        super(Local, self).__init__()

    def list_(self):
        raise NotImplementedError()

    def update(self, obj):
        raise NotImplementedError()

    def create(self, obj):
        raise NotImplementedError()

