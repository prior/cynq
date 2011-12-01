from uuid import uuid4
from .. import logging_helper
from . import BaseStore

class VoodooStoreObject(object): pass

class VoodooStore(BaseStore):
    def __init__(self, *args, **kwargs):
        self.keygen = kwargs.pop('keygen', (lambda dobj: str(uuid4())[0:8]))
        self.pre_fail = kwargs.pop('pre_fail', (lambda obj,op,tries: False))
        self.post_fail = kwargs.pop('post_fail', (lambda obj,op,tries: False))
        super(VoodooStore, self).__init__(*args, **kwargs)
        self.data = []
        self._obj_hash = None
        self._clear_stats()
        self.log = logging_helper.get_log('cynq.store.memory')
    
    def _dlist_convert(self, dobjs):
        return [self._dobj_convert(dobj) for dobj in dobjs]

    def _dobj_convert(self, dobj):
        obj = VoodooStoreObject()
        for attr in self.spec.attrs_with_key:
            if dobj.has_key(attr): setattr(obj, attr, dobj.get(attr))
        return obj

    def _obj_convert(self, obj):
        return dict((attr,getattr(obj,attr)) for attr in self.spec.attrs_with_key if hasattr(obj,attr))
    
    def _olist_convert(self, objs):
        return [self._obj_convert(obj) for obj in objs]

    def _get_obj_hash(self):
        if self._obj_hash is None: 
            self._obj_hash = dict((getattr(obj,self.key), obj) for obj in self.data if hasattr(obj,self.key))
        return self._obj_hash
    obj_hash = property(_get_obj_hash)

    def _all(self):
        self._pre(read=True)
        all_ = [obj for obj in self.data]
        self._post(read=True)
        return all_

    def _single_create(self, dobj):
        self._pre(create=dobj)
        if dobj.get(self.key) is None: dobj[self.key] = self.keygen(dobj)
        obj = self._dobj_convert(dobj)
        self.data.append(obj)
        self.obj_hash[dobj[self.key]] = obj
        self._post(create=self._obj_convert(obj))
        return obj

    def _single_update(self, key, obj, dchanges):
        self._pre(update=self._obj_convert(obj))
        for k,v in dchanges.iteritems():
            setattr(obj,k,v)
        if not key: self.obj_hash[getattr(obj,self.key)] = obj
        self._post(update=self._obj_convert(obj))
        return obj

    def _single_delete(self, key):
        obj = self.obj_hash[key]
        self._pre(delete=self._obj_convert(obj))
        self.data.remove(obj)
        del self.obj_hash[key]
        self._post(delete=self._obj_convert(obj))
        return obj

    def _pre(self, **kwargs):
        for op in ('read','create','update','delete'):
            if kwargs.get(op):
                dobj = kwargs.pop(op)
                self.pre_ops[op].append(dobj)
                if self.pre_fail(dobj,op,len(self.pre_ops[op])): raise StandardError("forced to throw an error")

    def _post(self, **kwargs):
        for op in ('read','create','update','delete'):
            if kwargs.get(op):
                dobj = kwargs.pop(op)
                self.post_ops[op].append(dobj)
                if self.post_fail(dobj,op,len(self.post_ops[op])): raise StandardError("forced to throw an error")

    def _get_pre_stats(self):
        return tuple(map(lambda op: len(self.pre_ops[op]),('read','create','update','delete')))
    pre_stats = property(_get_pre_stats)

    def _get_post_stats(self):
        return tuple(map(lambda op: len(self.post_ops[op]),('read','create','update','delete')))
    post_stats = property(_get_post_stats)

    def _get_stats(self):
        return (self.pre_stats, self.post_stats)
    stats = property(_get_stats)

    def _clear_stats(self):
        self.pre_ops={}; self.post_ops={}
        for op in ['read','create','update','delete']:
            self.pre_ops[op] = []
            self.post_ops[op] = []

    def _set_ddata(self, val): self.data = self._dlist_convert(val)
    def _get_ddata(self): return self._olist_convert(self.data)
    ddata = property(_get_ddata, _set_ddata)

    #def seed(self, count):
        #self.seeds = [self.build_seed() for i in xrange(count)]
        #self._hash = None
        #return self.seeds

    #def build_seed(self):
        #return dict((attr,str(uuid4())[:4]) for attr in self.attrs)


