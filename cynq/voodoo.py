from copy import copy
from spec.remote import RemoteSpec
from spec.local import LocalSpec
from uuid import uuid4

class VoodooMemoryApi(object):
    def __init__(self, key=None, attrs=None, pushed=None, seeds=None, push_lambda=None, pre_fail_lambda=None, post_fail_lambda=None):
        super(VoodooMemoryApi, self).__init__()
        self.key = key
        self.attrs = attrs
        self.pushed = pushed
        self.push_lambda = push_lambda or (lambda obj,attr,op: obj.get(attr) or "%s%s"%(attr,id(obj)))
        self.pre_fail_lambda = pre_fail_lambda or (lambda obj,op,tries: False)
        self.post_fail_lambda = post_fail_lambda or (lambda obj,op,tries: False)
        self.seeds = seeds or []
        self._hash = None
        self.clear_stats()
        self.clear_tries()

    def _get_hash(self):
        if self._hash is None: 
            self._hash = dict((o.get(self.key), o) for o in self.seeds)
        return self._hash
    hash_ = property(_get_hash)

    def all_(self):
        self._pre(read=True)
        self.tries['pre']['read'] +=1
        if self.pre_fail_lambda(None,'read',self.tries['pre']['read']): raise StandardError("forced to throw an error")
        list_ = [copy(o) for o in self.hash_.values()]
        self.tries['post']['read'] +=1
        if self.post_fail_lambda(None,'read',self.tries['post']['read']): raise StandardError("forced to throw an error")
        self._post(read=True)
        return list_

    def single_create(self, obj):
        _obj = self._copy_caring(obj)
        self._pre(create=_obj)
        self.tries['pre']['create'] +=1
        if self.pre_fail_lambda(_obj,'create',self.tries['pre']['create']): raise StandardError("forced to throw an error")
        for attr in self.pushed:
            _obj[attr] = self.push_lambda(_obj,attr,'create')
        self.hash_[_obj[self.key]] = _obj
        self.tries['post']['create'] +=1
        if self.post_fail_lambda(_obj,'create',self.tries['post']['create']): raise StandardError("forced to throw an error")
        for attr in _obj: obj[attr] = _obj[attr]
        self._post(create=_obj)
        return obj

    def single_update(self, obj):
        _obj = self._copy_caring(obj)
        self._pre(update=_obj)
        self.tries['pre']['update'] +=1
        if self.pre_fail_lambda(_obj,'update',self.tries['pre']['update']): raise StandardError("forced to throw an error")
        for attr in self.pushed:
            _obj[attr] = self.push_lambda(_obj,attr,'update')
        self.hash_[_obj[self.key]] = _obj
        self.tries['post']['update'] +=1
        if self.post_fail_lambda(_obj,'update',self.tries['post']['update']): raise StandardError("forced to throw an error")
        for attr in _obj: obj[attr] = _obj[attr]
        self._post(update=_obj)
        return obj

    def single_delete(self, obj):
        _obj = self._copy_caring(obj)
        self._pre(delete=_obj)
        self.tries['pre']['delete'] +=1
        if self.pre_fail_lambda(_obj,'delete',self.tries['pre']['delete']): raise StandardError("forced to throw an error")
        del self.hash_[_obj[self.key]]
        self.tries['post']['delete'] +=1
        if self.post_fail_lambda(_obj,'delete',self.tries['post']['delete']): raise StandardError("forced to throw an error")
        self._post(delete=_obj)

    def _copy_caring(self, obj):
        return dict((a,obj.get(a)) for a in self.attrs)

    def _pre(self, read=None, create=None, update=None, delete=None):
        if read: self.pre_read_count += 1
        if create: self.pre_create.append(copy(create))
        if update: self.pre_update.append(copy(update))
        if delete: self.pre_delete.append(copy(delete))

    def _post(self, read=None, create=None, update=None, delete=None):
        if read: self.post_read_count += 1
        if create: self.post_create.append(copy(create))
        if update: self.post_update.append(copy(update))
        if delete: self.post_delete.append(copy(delete))

    def _get_pre_stats(self):
        return (self.pre_read_count, len(self.pre_create), len(self.pre_update), len(self.pre_delete))
    pre_stats = property(_get_pre_stats)

    def _get_post_stats(self):
        return (self.post_read_count, len(self.post_create), len(self.post_update), len(self.post_delete))
    post_stats = property(_get_post_stats)

    def _get_stats(self):
        return {'pre':self.pre_stats, 'post':self.post_stats}
    stats = property(_get_stats)

    def clear_stats(self):
        self.pre_read_count = 0
        self.post_read_count = 0
        self.pre_create = []
        self.post_create = []
        self.pre_update = []
        self.post_update = []
        self.pre_delete = []
        self.post_delete = []

    def clear_tries(self):
        self.tries = dict((t,dict((op,0) for op in ('read','create','update','delete'))) for t in ('pre','post'))

    def seed(self, count):
        self.seeds = [self.build_seed() for i in xrange(count)]
        self._hash = None
        return self.seeds

    def build_seed(self):
        return dict((attr,str(uuid4())[:4]) for attr in self.attrs)



class VoodooBaseSpec(object):
    def __init__(self, voodoo_api):
        super(VoodooBaseSpec, self).__init__()
        self.api = voodoo_api

    def all_(self, *args, **kwargs): return self.api.all_(*args, **kwargs)
    def single_create(self, *args, **kwargs): return self.api.single_create(*args, **kwargs)
    def single_update(self, *args, **kwargs): return self.api.single_update(*args, **kwargs)
    def single_delete(self, *args, **kwargs): return self.api.single_delete(*args, **kwargs)

class VoodooRemoteSpec(VoodooBaseSpec, RemoteSpec):
    def __init__(self, voodoo_api):
        super(VoodooRemoteSpec,self).__init__(voodoo_api)
        voodoo_api.attrs = self.__class__._deduce_all_attrs()
        voodoo_api.key = self.__class__.key
        voodoo_api.pushed = self.__class__.pushed
        
class VoodooLocalSpec(VoodooBaseSpec, LocalSpec):
    def __init__(self, voodoo_api, remote_spec_classes):
        super(VoodooLocalSpec,self).__init__(voodoo_api)
        voodoo_api.attrs = self.__class__._deduce_all_attrs(remote_spec_classes)
        voodoo_api.key = self.__class__.key
        voodoo_api.pushed = self.__class__.extras

