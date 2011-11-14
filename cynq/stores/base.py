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


    def key_attribute_value(self, obj):
        return getattr(obj, self.key_attribute)

    def writeable_attributes(self):
        if not getattr(self, '_writeable_attributes', None):
            self._writeable_attributes = set(getattr(self, 'communal_attributes', []))
        return list(self._writeable_attributes)

    def readable_attributes(self):
        if not getattr(self, '_readable_attributes', None):
            attrs = set()
            attrs |= set(getattr(self,'communal_attributes',[]))
            attrs |= set(getattr(self,'owned_attributes',[]))
            self._readable_attributes = attrs
        return list(self._readable_attributes)

    def readables_seem_equal(self, obj1, obj2):
        return all(getattr(obj1,attr,None)==getattr(obj2,attr,None) for attr in self.readable_attributes())

    def writeables_seem_equal(self, obj1, obj2):
        return all(getattr(obj1,attr,None)==getattr(obj2,attr,None) for attr in self.writeable_attributes())

    def sets_seem_readably_equal(self, set1, set2):
        dict1 = dict((getattr(o,self.key_attribute),o) for o in set1 if getattr(o,self.key_attribute,None))
        dict2 = dict((getattr(o,self.key_attribute),o) for o in set2 if getattr(o,self.key_attribute,None))
        if set(dict1.keys()) != set(dict2.keys()):
            return False
        return all(self.readables_seem_equal(dict1[k],dict2[k]) for k in dict1.keys())

    def sets_seem_writeably_equal(self, set1, set2):
        dict1 = dict((getattr(o,self.key_attribute),o) for o in set1 if getattr(o,self.key_attribute,None))
        dict2 = dict((getattr(o,self.key_attribute),o) for o in set2 if getattr(o,self.key_attribute,None))
        if set(dict1.keys()) != set(dict2.keys()):
            return False
        return all(self.writeables_seem_equal(dict1[k],dict2[k]) for k in dict1.keys())

    def merge_writeables(self, target, source):
        for attr in self.writeable_attributes():
            setattr(target, attr, getattr(source, attr, None))
        return target

    def merge_readables(self, target, source):
        for attr in self.readable_attributes():
            setattr(target, attr, getattr(source, attr, None))
        return target
        
    def change_dict_if_merge_readables(self, target, source):
        """ if a merge were performed, what would the diff be? """
        change_dict = {}
        for attr in self.readable_attributes():
            if getattr(source, attr, None) != getattr(target, attr, None):
                change_dict[attr] = getattr(source, attr, None)
        return change_dict

    def change_dict_if_merge_writeables(self, target, source):
        """ if a merge were performed, what would the diff be? """
        change_dict = {}
        for attr in self.writeable_attributes():
            if getattr(source, attr, None) != getattr(target, attr, None):
                change_dict[attr] = getattr(source, attr, None)
        return change_dict

    def caring_dict(self, obj, *extras):
        caring_dict = {}
        for attr in self.readable_attributes() + list(extras):
            caring_dict[attr] = getattr(obj, attr, None)
        return caring_dict


        
