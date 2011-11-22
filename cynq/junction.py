import logging_helper
from sanetime import sanetime


class BaseStore(object):
    def __init__()
        self._object_list = None
        self._object_hash = None

    def _force_get_object_list(self):
        return self.spec.all_()

    def _get_list(self):
        if self._list is None:
            self._list = self.self._force_get_list()
        return self._list
    list_ = property(_get_list)

# for Remote
    def _get_hash(self):
        if self._hash is None:
            self._hash = dict((o[self.spec.key],o) for o in self.list_)
        return self._hash
    hash_ = property(_get_hash)

# for Local
    def get_object_hash(self, key):
        if self


    def 





            if self.remote_spec.since and self.remote_spec.sinceable and self.local_objects: 
                since = max(lo[self.remote_spec.since] for lo in self.local_objects)
                self._remote_objects = dict(
                    (self.
               self.max_since(self.remote_speclocal_objects = 

            else:

        return self._remote_objects
    objects = property(_get_objects)

class RemoteStore(object):
    def __init__(self, remote_spec):
        self.remote_spec = spec

    def _force_get_objects(self):
        if self.spec.sinceable and self.spec.since and self.local_objects: 
            since = max(lo[self.spec.since] for lo in self.local_objects)
            list
            self.spec.all_(since = since)
            objects = dict((self.speck.key for lo in self.
                    (self.
               self.max_since(self.remote_speclocal_objects = 
            
        else:
            return super(RemoteStore, self)._force_get_objects()


        else:
            
                self_remote_objects = self.remote_spec.all_()

        return self._remote_objects
    objects = property(_get_objects)


class Junction(object):
    def __init__(self, local_store, remote_store):
        super(Junction, self).__init__()
        self.log = logging_helper.get_log('cynq.junction')
        self.ls = local_store
        self.rs = remote_store
        self._remote_objects = None

    def _get_remote_objects(self):
        if self._remote_objects is None:
            if self.remote_spec.since and self.remote_spec.sinceable and self.local_objects: 
                since = max(lo[self.remote_spec.since] for lo in self.local_objects)
                self._remote_objects = dict(
                    (self.
               self.max_since(self.remote_speclocal_objects = 

            else:
                self_remote_objects = self.remote_spec.all_()

        return self._remote_objects
    remote_objects = property(_get_remote_objects)

    def _get_local_objects(self):
        if self._local_objects is None:
            self._local_objects = self.local_spec.all_()
        return self._remote_objects
    local_objects = property(_get_local_objects)



    intersection

    local_create = 
    local_update = 
    local_delete = 
    remote_delete =
    remote

    def intersection(

    def locals_not_in_remote(no_errors=True, deleted_at=None):
        objs = list(self.local_store.all_())
        if no_errors:
            for i in xrange(len(objs),0,-1):
                if objs[i].get('_errors',{}).get(self.rs,[]):
                    objs.pop(i)

        if deleted_at:
            for i in xrange(len(objs),0,-1):
                if objs[i].get('_errors',{}).get


        for local_obj in self.local_store.all_():


            if not obj.get('_errors',{}).get(self.rs,[]): # no errors associated to this remote store
                if not obj.get('deleted_at'): # and not deleted


            (rs):

            key_value = self.rs.key_value(local_obj)
            if not key_value or key_value not in self.rs.key_values:

                if not self.connection.get_remote_expectation(local_obj):

    def remotes_not_in_locals(deleted_at=None):

        for local_obj in self.local_store.all_(deleted_at


