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

        attrs = set()
        attrs |= set(getattr(self,'communal_attributes',[]))
        attrs |= set(getattr(self,'owned_attributes',[]))
        if getattr(self,'key_attribute',None):
            if getattr(self,'key_attribute') not in attrs:
                raise Exception("gotta have your key set also as a communal or an owned")


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


    def inbound_attributes(self):
        if not getattr(self, '_inbound_attributes', None):
            self._inbound_attributes = set(getattr(self, 'communal_attributes', []))
        return self._inbound_attributes

    def outbound_attributes(self):
        if not getattr(self, '_outbound_attributes', None):
            attrs = set()
            attrs |= set(getattr(self,'communal_attributes',[]))
            attrs |= set(getattr(self,'owned_attributes',[]))
            self._outbound_attributes = attrs
        return self._outbound_attributes

    # as seen through the lens of this remote
    def objects_seem_equal(self, obj1, obj2):
        return all(getattr(obj1,attr,None)==getattr(obj2,attr,None) for attr in self.outbound_attributes())

    # as seen through the lens of this remote
    def sets_seem_equal(self, set1, set2):
        dict1 = dict((getattr(o,self.key_attribute),o) for o in set1 if getattr(o,self.key_attribute,None))
        dict2 = dict((getattr(o,self.key_attribute),o) for o in set2 if getattr(o,self.key_attribute,None))
        if set(dict1.keys()) != set(dict2.keys()):
            return False
        return all(self.objects_seem_equal(dict1[k],dict2[k]) for k in dict1.keys())

    def inbound_merge(self, target, source):
        for attr in self.inbound_attributes():
            setattr(target, attr, getattr(source, attr, None))
        return target

    def outbound_merge(self, target, source):
        for attr in self.outbound_attributes():
            setattr(target, attr, getattr(source, attr, None))
        return target
        
        
