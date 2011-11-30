#from spec.remote import RemoteSpec
#from spec.local import LocalSpec
from uuid import uuid4
from cynq import logging_helper
from cynq.store import BaseStore

class VoodooMemoryStoreObject(object): pass

class VoodooMemoryStore(BaseStore):
    def __init__(self, *args, **kwargs):
        self.data = self._dconvert(kwargs.pop('dseeds') or [])
        self.keygen = kwargs.pop('keygen') or (lambda dobj: str(uuid4())[0:8])
        self.pre_fail = kwargs.pop('pre_fail') or (lambda obj,op,tries: False)
        self.post_fail = kwargs.pop('post_fail') or (lambda obj,op,tries: False)
        super(BaseStore, self).__init__(*args, **kwargs)
        self._obj_hash = None
        self.log = logging_helper.get_log('cynq.store.memory')
    
    def _dlist_convert(self, dobjs):
        return [self._dobj_convert(dobj) for dobj in dobjs]

    def _dobj_convert(self, dobj):
        obj = VoodooMemoryStoreObject()
        for attr in self.spec.attrs_with_key:
            if dobj.has_key(attr): setattr(obj, attr, dobj.get(attr))
        return obj

    def _obj_convert(self, obj):
        return dict((attr,getattr(obj,attr)) for attr in self.spec.attrs_with_key if hasattr(obj,attr))
    
    def _obj_list_convert(self, objs):
        return [self._obj_convert(obj) for obj in objs]

    def _get_obj_hash(self):
        if self._obj_hash is None: 
            self._obj_hash = dict((getattr(obj,self.key), obj) for obj in self.seeds if hasattr(obj,self.key))
        return self._obj_hash
    obj_hash = property(_get_obj_hash)

    def all_(self):
        self._pre(read=True)
        data = self.data
        self._post(read=True)
        return data

    def single_create(self, dobj):
        self._pre(create=dobj)
        if not dobj.has_key(self.key): dobj[self.key] = self.keygen(dobj)
        obj = self._dobj_convert(dobj)
        self.data.append(obj)
        self.obj_hash[dobj[self.key]] = obj
        self._post(create=self._obj_convert(obj))
        return obj

    def single_update(self, key, dchanges):
        obj = self.obj_hash[key]
        self._pre(update=self._obj_convert(obj))
        for k,v in dchanges.iteritems():
            setattr(obj,k,v)
        self._post(delete=self._obj_convert(obj))
        return obj

    def single_delete(self, key):
        obj = self.obj_hash[key]
        self._pre(update=self._obj_convert(obj))
        self.data.remove(obj)
        del self.obj_hash[key]
        self._post(delete=self._obj_convert(obj))
        return obj

    def _pre(self, **kwargs):
        for op in ('read','create','update','delete'):
            if kwargs.get(op):
                dobj = kwargs.pop(op)
                self.pre_ops[op].append(dobj)
                if self.pre_fail_lambda(dobj,op,len(self.ops[op])): raise StandardError("forced to throw an error")

    def _post(self, **kwargs):
        for op in ('read','create','update','delete'):
            if kwargs.get(op):
                dobj = kwargs.pop(op)
                self.post_ops[op].append(dobj)
                if self.post_fail_lambda(dobj,op,len(self.ops[op])): raise StandardError("forced to throw an error")

    def _get_pre_stats(self):
        return tuple(map(lambda op: len(self.pre_ops[op]),('read','create','update','delete')))
    pre_stats = property(_get_pre_stats)

    def _get_post_stats(self):
        return tuple(map(lambda op: len(self.post_ops[op]),('read','create','update','delete')))
    post_stats = property(_get_post_stats)

    def _get_stats(self):
        return (self.pre_stats, self.post_stats)
    stats = property(_get_stats)

    def clear_stats(self):
        for op in ['read','create','update','delete']:
            self.pre_ops[op] = []
            self.post_ops[op] = []

    #def seed(self, count):
        #self.seeds = [self.build_seed() for i in xrange(count)]
        #self._hash = None
        #return self.seeds

    #def build_seed(self):
        #return dict((attr,str(uuid4())[:4]) for attr in self.attrs)



#class VoodooBaseSpec(object):
    #def __init__(self):
        #super(VoodooBaseSpec, self).__init__()
        #self.api = VoodooMemoryApi()
        #for conf in ['key','pushed','seeds','push_lambda','pre_fail_lambda','post_fail_lambda']:
            #setattr(self.api, conf, getattr(self.__class__,conf, getattr(self.api,conf)))

    #def all_(self, *args, **kwargs): return self.api.all_(*args, **kwargs)
    #def single_create(self, *args, **kwargs): return self.api.single_create(*args, **kwargs)
    #def single_update(self, *args, **kwargs): return self.api.single_update(*args, **kwargs)
    #def single_delete(self, *args, **kwargs): return self.api.single_delete(*args, **kwargs)

#class VoodooRemoteSpec(VoodooBaseSpec, RemoteSpec):
    #def __init__(self):
        #super(VoodooRemoteSpec,self).__init__()
        #self.api.attrs = self.__class__._deduce_all_attrs()
        
#class VoodooLocalSpec(VoodooBaseSpec, LocalSpec):
    #def __init__(self, remote_spec_classes):
        #super(VoodooLocalSpec,self).__init__()
        #self.api.attrs = self.__class__._deduce_all_attrs(remote_spec_classes)

