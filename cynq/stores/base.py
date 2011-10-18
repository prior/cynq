STORE_DESIGNATIONS = [
    'key_attribute',
    'communal_attributes',
    'owned_attributes',
    'remote_expectation_attribute' ]  # only expect this last one on remote stores

class Base(object):
    def __init__(self):
        for attr in STORE_DESIGNATIONS:  # bring designations into instance fields
            if getattr(self.__class__, attr, None):
                setattr(self, attr, getattr(self.__class__, attr))

    def get(self, id_):
        raise NotImplementedError()

    def list_(self):
        raise NotImplementedError()

    def update(self, obj):
        raise NotImplementedError()

    def create(self, obj):
        raise NotImplementedError()

    def delete(self, obj):
        raise NotImplementedError()


