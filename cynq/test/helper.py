import unittest2
from copy import deepcopy
#from pprint import pprint

class TestCase(unittest2.TestCase):
    def assert_equal_dlists(self, dlist1, dlist2, remove_attrs=None):
        if remove_attrs:
            dlist1 = self.remove_attrs_in_list(deepcopy(dlist1), remove_attrs)
            dlist2 = self.remove_attrs_in_list(deepcopy(dlist2), remove_attrs)
        t1,t2 = self._to_tuples(dlist1,dlist2)
        self.assertEqual(t1,t2)

    def assert_not_equal_dlists(self, dlist1, dlist2):
        t1,t2 = self._to_tuples(dlist1,dlist2)
        self.assertNotEqual(t1,t2)

    def _to_tuples(self, l1, l2):
        t1 = tuple(sorted(tuple(sorted(o.iteritems())) for o in l1))
        t2 = tuple(sorted(tuple(sorted(o.iteritems())) for o in l2))
        return (t1,t2)

    def _remove_attrs_in_list(self, list_, attrs):
        for o in list_:
            for a in attrs:
                if o.has_key(a): 
                    del o[a]
        return list_
    

