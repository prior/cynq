STORE_DESIGNATIONS = set([
    'key_attribute',
    'communal_attributes',
    'owned_attributes',
    'remote_expectation_attribute' ])  # only expect this last one on remote stores

class Base(object):
    def __init__(self):
        for designation in STORE_DESIGNATIONS:  # bring designations into instance fields
            if getattr(self.__class__, designation, None):
                setattr(self, designation, getattr(self.__class__, designation))

    def get(self, id_):
        raise NotImplementedError()

    def all_(self):
        raise NotImplementedError()

    def update(self, obj):
        raise NotImplementedError()

    def create(self, obj):
        raise NotImplementedError()

    def delete(self, obj):
        raise NotImplementedError()

    @classmethod
    def understood_attributes(cls):
        designations = STORE_DESIGNATIONS - set(['remote_expectation_attribute'])
        attrs = set()
        for designation in designations:  # bring designations into instance fields
            if getattr(cls, designation, None):
                attrs = attrs | set(getattr(cls, designation))
        return attrs

        

