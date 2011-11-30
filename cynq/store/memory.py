#from spec.remote import RemoteSpec
#from spec.local import LocalSpec
from uuid import uuid4
import logging_helper

from store import BaseStore

class MemoryStoreObject(object): pass

class MemoryStore(BaseStore):
    def __init__(self, *args, **kwargs):
        self.data = self._dconvert(kwargs.pop('dseeds') or [])
        self.keygen = kwargs.pop('keygen') or (lambda dobj: str(uuid4())[0:8])
        super(BaseStore, self).__init__(*args, **kwargs)
        self._obj_hash = None
        self.log = logging_helper.get_log('cynq.store.memory')
    
    def all_(self):
        data = self.data
        return data

    def single_create(self, dobj):
        if not dobj.has_key(self.key): dobj[self.key] = self.keygen(dobj)
        obj = self._dobj_convert(dobj)
        self.data.append(obj)
        self.obj_hash[dobj[self.key]] = obj
        return obj

    def single_update(self, key, dchanges):
        obj = self.obj_hash[key]
        for k,v in dchanges.iteritems():
            setattr(obj,k,v)
        return obj

    def single_delete(self, key):
        obj = self.obj_hash[key]
        self.data.remove(obj)
        del self.obj_hash[key]
        return obj

    def _dlist_convert(self, dlist):
        data = []
        for d in dlist:
            data.append(self._dobj_convert(d))
        return data

    def _dobj_convert(self, dobj):
        obj = MemoryStoreObject()
        for attr in self.spec.attrs_with_key:
            if dobj.has_key(attr): setattr(obj, attr, dobj.get(attr))
        return obj

    def _obj_convert(self, obj):
        return dict((attr,getattr(obj,attr)) for attr in self.spec.attrs_with_key if hasattr(obj,attr))

    def _get_obj_hash(self):
        if self._obj_hash is None: 
            self._obj_hash = dict((getattr(obj,self.key), obj) for obj in self.seeds if hasattr(obj,self.key))
        return self._obj_hash
    obj_hash = property(_get_obj_hash)

