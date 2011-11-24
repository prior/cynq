import copy
from cynq.spec.remote import RemoteSpec
from cynq.spec.local import LocalSpec

class VoodooMemoryApi(object):
    def __init__(self, seeds=None, key_attr=None, since_attr=None, push_gen=None, pre_fail_gen=None, post_fail_gen=None):
        super(VoodooMemoryApi, self).__init__()
        self.key = key_attr
        self.since = since_attr
        self.push_gen = push_gen or (lambda obj,attr,op: "%s%s"%(attr,id(obj)))
        self.pre_fail_gen = pre_fail_gen or (lambda obj,op: False)
        self.post_fail_gen = post_fail_gen or (lambda obj,op: False)
        self.hash_ = dict((o.get(self.key), o) for o in seeds)

    def all_(self, since=None):
        self._pre(read=True)
        if self.pre_fail_gen(None,'read'): raise StandardError("forced to throw an error")
        list_ = [copy(o) for o in self.hash_.values() if not since or o.get(self.since) and since>=o.get(self.since)]
        if self.post_fail_gen(None,'read'): raise StandardError("forced to throw an error")
        self._pre(read=True)
        return list_

    def single_create(self, obj):
        _obj = copy(obj)
        self._pre(create=_obj)
        if self.pre_fail_gen(_obj,'create'): raise StandardError("forced to throw an error")
        for attr in self.pushed:
            _obj[attr] = self.push_gen(_obj,attr)
        self.hash_[_obj[self.key]] = _obj
        if self.post_fail_gen(_obj,'create'): raise StandardError("forced to throw an error")
        for attr in _obj: obj[attr] = _obj[attr]
        self._post(create=_obj)
        return obj

    def single_update(self, obj):
        _obj = copy(obj)
        self._pre(update=_obj)
        if self.pre_fail_gen(_obj,'update'): raise StandardError("forced to throw an error")
        for attr in self.pushed:
            _obj[attr] = self.push_gen(_obj,attr)
        self.hash_[_obj[self.key]] = _obj
        if self.post_fail_gen(_obj,'update'): raise StandardError("forced to throw an error")
        for attr in _obj: obj[attr] = _obj[attr]
        self._post(update=_obj)
        return obj

    def single_delete(self, obj):
        _obj = copy(obj)
        self._pre(delete=_obj)
        if self.pre_fail_gen(_obj,'delete'): raise StandardError("forced to throw an error")
        del self.hash_[_obj[self.key]]
        if self.post_fail_gen(_obj,'delete'): raise StandardError("forced to throw an error")
        self._post(delete=_obj)

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


class VoodooBaseSpec(object):
    def __init(self, voodoo_api):
        super(VoodooBaseSpec, self).__init__()
        self.api = voodoo_api

    def all_(self, *args, **kwargs): return self.api.all_(*args, **kwargs)
    def single_create(self, *args, **kwargs): return self.api.single_create(*args, **kwargs)
    def single_update(self, *args, **kwargs): return self.api.single_update(*args, **kwargs)
    def single_delete(self, *args, **kwargs): return self.api.single_delete(*args, **kwargs)

class VoodooRemoteSpec(RemoteSpec, VoodooBaseSpec):
    def __init__(self, voodoo_api):
        super(VoodooRemoteSpec,self).__init__(voodoo_api)

class VoodooLocalSpec(LocalSpec, VoodooBaseSpec):
    def __init__(self, voodoo_api):
        super(VoodooLocalSpec,self).__init__(voodoo_api)

