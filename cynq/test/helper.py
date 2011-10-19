import unittest2
import uuid
from cynq.stores.base import Base


class TestObject(object):
    attrs = []
    prepopulate_attributes = False

    def __init__(self, *args, **kwargs):
        super(TestObject,self).__init__()
        if self.__class__.prepopulate_attributes:
            args = list(args or self.__class__.attrs)
        self.change(args)
        for k in kwargs:
            setattr(self,k,kwargs[k])

    def change(self, attrs=None):
        attrs = attrs or []
        for attr in attrs:
            setattr(self, attr, str(uuid.uuid4())[:16])

    @classmethod
    def random(cls, *args):
        attrs = list(args)
        if len(attrs)==0 and len(cls.attrs)>0:
            attrs = list(cls.attrs)
        obj = cls()
        obj.change(attrs)


class TestStore(Base):
    def __init__(self):
        super(TestStore,self).__init__()
        self.creates = []
        self.updates = []
        self.deletes = []
        self.all_calls = 0 

    def all_(self):
        self.all_calls += 1
        return getattr(self,'_all',set())

    def create(self, obj):
        self.creates.append(obj)
        return obj

    def update(self, obj):
        self.updates.append(obj)
        return obj

    def delete(self, obj):
        self.deletes.append(obj)
        return obj



class TestCase(unittest2.TestCase):
    def assert_store_changes(self, store, creates=None, updates=None, deletes=None, all_calls=None):
        creates = creates or []
        updates = updates or []
        deletes = deletes or []
        self.assertEquals(set(creates), set(store.creates))
        self.assertEquals(set(updates), set(store.updates))
        self.assertEquals(set(deletes), set(store.deletes))
        if all_calls is not None:
            self.assertEquals(all_calls, store.all_calls)


