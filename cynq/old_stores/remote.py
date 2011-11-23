import base

# override this class, specify the class attributes, and implement the crud methods
class Remote(base.Base):
    communal_attributes = []
    owned_attributes = []
    key_attribute = None
    remote_expectation_attribute = None

    def __init__(self):
        super(Remote, self).__init__()

    def all_(self):
        raise NotImplementedError()

    def update(self, obj):
        raise NotImplementedError()

    def create(self, obj):
        raise NotImplementedError()

    def delete(self, obj):
        raise NotImplementedError()
