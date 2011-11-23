import copy
import logging_helper
from error import StoreError


class TestMemorySpec(Base):
    def __init__(self, seeds=None, key=None, push_gen=None):
        super(TestMemorySpec, self).__init__()
        self.hash_ = self.hashify_list(seeds or [])
        self.push_gen = push_gen
        self.crud_stats = (0,0,0,0)
        self.hash_ = dict((o.get(self.key), o) for o in self.all_())

    def all_(self):
        self._pre(read=True)
        list_ = self.hash_.values()
        self._pre(read=True)
        return list_

    def single_create(self, obj):
        self._pre(create=obj)
        for attr in self.pushed:
            obj[attr] = self.push_gen(attr)
        self.hash_[obj[self.key]] = obj
        self._post(create=obj)
        return obj

    def single_update(self, obj):
        self._pre(update=obj)
        for attr in self.pushed:
            if obj.get(attr) is None:
                obj[attr] = self.push_gen(attr)
        self.hash_[obj[self.key]] = obj
        self._post(update=obj)
        return obj

    def single_delete(self, obj):
        self._pre(delete=obj)
        del self.hash_[obj[self.key]]
        self._post(delete=obj)

    def _pre(self, read=False, create=False, update=False, delete=False):
        for change_type in ['create', 'update', 'delete']:
            if locals().get(change_type):
                list_ = getattr(self, "%ss_before"%change_type, [])
                list_.append(copy(locals().get(change_type)))
                setattr(self, "%ss_before"%change_type, list_)

    def _post(self, read=False, create=False, update=False, delete=False):
        self.crud_stats = (
            self.crud_stats[0] + (read and 1 or 0),
            self.crud_stats[1] + (create and 1 or 0),
            self.crud_stats[2] + (update and 1 or 0),
            self.crud_stats[3] + (delete and 1 or 0) )
        for change_type in ['create', 'update', 'delete']:
            if locals().get(change_type):
                list_ = getattr(self, "%ss_after"%change_type, [])
                list_.append(copy(locals().get(change_type)))
                setattr(self, "%ss_after"%change_type, list_)



