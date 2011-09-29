class BaseStore(object):
    key_attribute = None
    owned_attributes = []
    syncable_attributes = []

    def __init__(self):
        self.clear_cache()
        self.owned_attributes = self.__class__.owned_attributes
        self.syncable_attributes = self.__class__.syncable_attributes
        self.key_attribute = self.__class__.key_attribute

    def get(self, id_):
        return self._get(id_)

    def get_id(self, obj, *args):
        return getattr(obj, self.key_attribute, *args)

    def clear_cache(self):
        self._cached_list = None
        self._cached_hash = None

    def cached_list(self):
        if self._cached_list == None:
            self._cached_list = self._list()
            self._cached_hash = {}
            for obj in self._cached_list:
                self._cached_hash[self.get_id(obj)] = obj
        return self._cached_list

    def cached_hash(self):
        if self._cached_hash == None:
            self.cached_list()
        return self._cached_hash

    def _adjust_cache(self, creates=None, updates=None, deletes=None):
        if self._cached_list != None:
            if updates:
                for obj in updates:
                    self._cached_list.remove(self._cached_hash[self.get_id(obj)])
                    self._cached_list.append(obj)
                    self._cached_hash[self.get_id(obj)] = obj
            if creates:
                for obj in creates:
                    self._cached_list.append(obj)
                    self._cached_hash[self.get_id(obj)] = obj
            if deletes:
                for obj in deletes:
                    self._cached_list.remove(self._cached_hash[self.get_id(obj)])
                    del self._cached_hash[self.get_id(obj)]

    def list_(self, clear_cache=False):
        if clear_cache:
            self.clear_cache()
        return self.cached_list()

    def save(self, obj):
        if self.get_id(obj, None):
            obj = self._update(obj)
            self._adjust_cache(updates=[obj])
        else:
            for attr in self.owned_attributes:
                if getattr(obj, attr, None):
                    raise Exception('attempt to assign owned attribute!')
            obj = self._create(obj)
            self._adjust_cache(creates=[obj])
        self._persisted(obj)
        return obj

    def delete(self, obj):
        obj = self._delete(obj)
        self._adjust_cache(deletes=[obj])
        self._persisted(obj)

    def sync_prep(self, sync_time):
        self.clear_cache()
        self.sync_time = sync_time

    def _persisted(self, obj):
        if getattr(obj, '_updated', False):
            del obj._updated
        
    def _delete(self, obj):
        raise Exception("Not Implemented!") 

    def _get(self, id_):
        raise Exception("Not Implemented!") 

    def _list(self):
        raise Exception("Not Implemented!") 

    def _update(self, obj):
        raise Exception("Not Implemented!") 

    def _create(self, obj):
        raise Exception("Not Implemented!") 
