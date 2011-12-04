from uuid import uuid4
from .. import logging_helper
from . import BaseStore

class VoodooStoreObject(object): pass

class VoodooStore(BaseStore):
    def __init__(self, *args, **kwargs):
        self.keygen = kwargs.pop('keygen', (lambda dobj: str(uuid4())[0:8]))
        self.pushgen = kwargs.pop('pushgen', (lambda dobj: str(uuid4())[0:8]))
        self.pre_fail = kwargs.pop('pre_fail', (lambda obj,op,tries: False))
        self.post_fail = kwargs.pop('post_fail', (lambda obj,op,tries: False))
        spec = kwargs.pop('spec', None)
        if spec: 
            kwargs['attrs'] = set(list(spec.rpushed) + list(spec.rpulled) + list(spec.shared))
            kwargs['key'] = spec.key
            kwargs['push_attrs'] = spec.rpushed
        self.attrs = kwargs.pop('attrs', [])
        self.vkey = kwargs.pop('key')
        self.push_attrs = kwargs.pop('push_attrs',[])
        super(VoodooStore, self).__init__(*args, **kwargs)
        self.data = []
        self._obj_hash = None
        self._clear_stats()
        self.log = logging_helper.get_log('cynq.store.memory')
    
    def _dlist_convert(self, dobjs):
        return [self._dobj_convert(dobj) for dobj in dobjs]

    def _dobj_convert(self, dobj):
        obj = VoodooStoreObject()
        for attr in self.attrs:
            if dobj.has_key(attr): setattr(obj, attr, dobj.get(attr))
        return obj

    def _obj_convert(self, obj):
        return dict((attr,getattr(obj,attr)) for attr in self.attrs if hasattr(obj,attr))
    
    def _olist_convert(self, objs):
        return [self._obj_convert(obj) for obj in objs]

    def _get_obj_hash(self):
        if self._obj_hash is None: 
            self._obj_hash = dict((getattr(obj,self.vkey), obj) for obj in self.data if hasattr(obj,self.vkey))
        return self._obj_hash
    obj_hash = property(_get_obj_hash)

    def _all(self):
        self._pre(read=True)
        all_ = [obj for obj in self.data]
        self._post(read=True)
        return all_

    def _single_create(self, dobj):
        self._pre(create=dobj)
        if dobj.get(self.vkey) is None: dobj[self.vkey] = self.keygen(dobj)
        for attr in self.push_attrs:
            if not dobj.get(attr): dobj[attr] = self.pushgen(dobj)
        for attr in self.attrs:
            if not dobj.has_key(attr): dobj[attr] = None
        obj = self._dobj_convert(dobj)
        self.data.append(obj)
        self.obj_hash[dobj[self.vkey]] = obj
        self._post(create=self._obj_convert(obj))
        return obj

    def _single_update(self, obj, dchanges):
        self._pre(update=self._obj_convert(obj))
        for k,v in dchanges.iteritems():
            setattr(obj,k,v)
        self.obj_hash[getattr(obj,self.vkey)] = obj
        self._post(update=self._obj_convert(obj))
        return obj

    def _single_delete(self, obj):
        self._pre(delete=self._obj_convert(obj))
        self.data.remove(obj)
        if getattr(obj, self.vkey) in self.obj_hash: del self.obj_hash[getattr(obj, self.vkey)]
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

    def generate_seeds(self, count):
        self.ddata = [self._build_dseed() for i in xrange(count)]

    def _build_dseed(self):
        return dict((attr,str(uuid4())[:8]) for attr in self.attrs)

    def _get_backward_translated_ddata(self): return [self._bulk_backward_translate(d) for d in self.ddata]
    backward_translated_ddata = property(_get_backward_translated_ddata)


