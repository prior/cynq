class BaseMemoryObject(object):
    attrs = ()
    def __init__(self, **kwargs):
        for attr in self.__class__.attrs:
            setattr(self, attr, kwargs.get(attr))

