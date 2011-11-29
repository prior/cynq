from cynq.error import Error

#important! do not expect these to change during execution!  need to get that in the docs (if you do change them those changes likey won't be honored)
 
# inherit from this to specify your cynq config

ATTR_COMPONENTS = ('rpushed', 'rpulled', 'shared')

class Spec(object):

    # overrideable specs
    rpushed = ()  # list of items that are generated by this remote and can never be written to this remote
    rpulled = ()  # lsit of items that are written to this remote and are never generated by this remote
    shared = ()  # list of items that can be written by both sides
    key = None  # the key attribute to use when comparing

    # private methods
    def __init__(self):
        super(Spec,self).__init__()
        for conf in ATTR_COMPONENTS:
            setattr(self, conf, set(getattr(self.__class__, conf, ())))
        self.key = self.__class__.key
        self.attrs = set(attr for conf in ATTR_COMPONENTS for attrs in getattr(self, conf) for attr in attrs)
        self.attrs_with_key = list(self.attrs) + [self.key]
        self.attrs_without_key = list(self.attrs) + [self.key]
        self._assert_valid_spec()
        self.key_remotely_generated = self.key in self.remotely_generated

    def _assert_valid_spec(self):
        individual_sum = sum(len(getattr(self,conf)) for conf in ATTR_COMPONENTS)
        set_sum = len(self.attrs)
        if individual_sum != set_sum:
            raise Error("Spec doesn't make sense -- there is overlap in the attrs")
        if self.key and self.key not in self.attrs:
            raise Error("Spec doesn't make sense -- key not in set of possible attrs")


