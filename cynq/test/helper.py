from copy import deepcopy

def assert_equal_object_lists(self, list1, list2, remove_attrs=None):
    if remove_attrs:
        list1 = self.remove_attrs_in_list(deepcopy(list1), remove_attrs)
        list2 = self.remove_attrs_in_list(deepcopy(list2), remove_attrs)
    t1,t2 = self._to_tuples(list1,list2)
    self.assertEquals(t1,t2)

def assert_not_equal_object_lists(self, list1, list2):
    t1,t2 = self._to_tuples(list1,list2)
    self.assertNotEquals(t1,t2)

def remove_attrs_in_list(self, list_, attrs):
    for o in list_:
        for a in attrs:
            if o.has_key(a): 
                del o[a]
    return list_
    
def _to_tuples(self, l1, l2):
    t1 = tuple(sorted(tuple(sorted(o.iteritems())) for o in l1))
    t2 = tuple(sorted(tuple(sorted(o.iteritems())) for o in l2))
    return (t1,t2)

