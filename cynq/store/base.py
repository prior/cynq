from cynq.error import Error,StoreError
from cynq import logging_helper
from traceback import format_exc

#TODO: test cached levels

class BaseStore(object):
    SPEC_FIELD_PROXIES = ('key',)

    def __init__(self, spec):
        super(BaseStore, self).__init__()
        self.spec = spec
        self.clear_caches()
        self.clear_change_queue()
        self.clear_stats()
        self._build_spec_proxies()
        self.log = logging_helper.get_log('cynq.store.%s'%self.spec.name)

    def clear_change_queue(self):
        self._queued = {'creates':[], 'updates':[], 'deletes':[]}

    def clear_stats(self):
        self._stats = {'creates':{True:0,False:0}, 'updates':{True:0,False:0}, 'deletes':{True:0,False:0}}

    def _build_spec_proxies(self):
        for field in self.__class__.SPEC_FIELD_PROXIES:
            setattr(self, field, getattr(self.spec, field))

    def _force_get_list(self):
        return self.spec.all_()

    def _get_list(self):
        if self._list is None:
            self._list = self._force_get_list()
        return self._list
    list_ = property(_get_list)

    def _force_build_hash(self, key_attr):
        return dict((o[key_attr],o) for o in self.list_ if o.get(key_attr) is not None)

    def get_hash(self, key_attr):
        if self._hashes.get(key_attr) is None:
            self._hashes[key_attr] = self._force_build_hash(key_attr)
        return self._hashes[key_attr]

    def clear_caches(self):
        self._hashes = {} 
        self._list = None

    # playing with objects in that exist in the _list
    def create(self, obj): return self.change(obj, 'create')
    def update(self, obj): return self.change(obj, 'update')
    def delete(self, obj): return self.change(obj, 'delete')
    def change(self, obj, change_type):
        self._queued['%ss'%change_type].append(obj)
        getattr(self,'_%sd'%change_type)(obj)
        
    def unique_object_list(self, lst):
        x = dict((id(o),o) for o in lst).values()
        return x
    

    def persist_changes(self):
        for change_type in ['create','update','delete']:
            self._queued['%ss'%change_type] = self.unique_object_list(self._queued['%ss'%change_type])
        for o in self._queued['creates']:
            if o in self._queued['updates']: self._queued['updates'].remove(o)
        if set(id(o) for o in self._queued['deletes']) & set(id(o) for o in self._queued['creates']): raise Error("shouldn't have creates and deletes on same backing store in same cynq")
        results = {}
        for change_type in ['create','update','delete']:
            queue = self._queued['%ss'%change_type]
            if queue:
                (successes, errors, leftovers) = getattr(self,'batch_%s'%change_type)(queue)
                if errors: # can't be sure if errors happened after or before changes, so gotta wipe caches and force relisting
                    self.clear_caches()
                elif self._hashes.get(self.key) is not None:
                    del self._hashes[self.key]
                results[change_type] = (successes, errors, leftovers)
        self.clear_change_queue()
        return results

    def _created(self, obj):
        self.list_.append(obj)
        for key in self._hashes:
            hash_ = self._hashes[key]
            key_value = obj.get(key)
            if key_value is not None:
                if key_value in hash_: raise Error("key already exists!")  #_TODO: embellish
                if obj in hash_.values(): raise Error("obj already in hash!")  #_TODO: embellish
                hash_[key_value] = obj

#_TODO: figure out implications of an update of a key attribute-- should we be disallowing such an action
    def _updated(self, obj):
        if obj not in self.list_: raise Error("expecting an object I own!")
        for key in self._hashes:
            hash_ = self._hashes[key]
            key_value = obj.get(key)
            if key_value is None:
                if obj in hash_.values():
                    fishing_key = None
                    for (k,v) in hash_.iteritems():
                        if v==obj: fishing_key = k; break
                    del hash_[fishing_key]
            else:
                if key_value in hash_ and hash_[key_value] != obj: 
                    raise Error("object already exists for that key and it's not this one!")  #_TODO: embellish
                if obj not in hash_.values():
                    hash_[key_value] = obj

    def _deleted(self, obj): 
        if obj not in self.list_: raise Error("expecting to delete an object I own!")
        self.list_.remove(obj)
        for key in self._hashes:
            hash_ = self._hashes[key]
            key_value = obj.get(key)
            if key_value is not None:
                if obj not in hash_.values(): raise Error("obj should be in the hash!")  #_TODO: embellish
                del hash_[key_value]


    #proxy spec functions with proper exception handling
    def all_(self, *args, **kwargs):
        try: self.spec._all(*args, **kwargs)
        except StandardError as err: raise StoreError(self, err)

    def single_create(self, obj): return self._single_change('create', obj)
    def single_update(self, obj): return self._single_change('update', obj)
    def single_delete(self, obj): return self._single_change('delete', obj)
    def _single_change(self, change_type, obj):
        try: 
            return getattr(self.spec, 'single_%s'%change_type)(obj)
        except StandardError as err: 
            obj.setdefault('_error', {})[self.spec.name] = err
            self.log.error(format_exc(err))
            raise StoreError(self, format_exc(err))

    #proxy spec functions with proper exception handling
    def batch_create(self, objs): return self._batch_change('create', objs)
    def batch_update(self, objs): return self._batch_change('update', objs)
    def batch_delete(self, objs): return self._batch_change('delete', objs)
    def _batch_change(self, change_type, objs):
        batch_method = getattr(self.spec, 'batch_%s'%change_type)
        try:
            batch_method([])
        except NotImplementedError:
            batch_method = getattr(self, '_batch_change_using_singles')

        results = ([],[],objs)
        while len(results[2]):
            results = batch_method(change_type, results[2])
            self._stats['%ss'%change_type][True] += len(results[0])
            self._stats['%ss'%change_type][False] += len(results[1])
            for obj in results[0]: obj['_%sd'%change_type] = True
            for obj in results[1]: obj.setdefault('_error',{}).setdefault(self.spec.name,True)
            if self._is_too_many_failures(len(results[0]) + len(results[1]), len(results[1])):
                raise StoreError("Too many failures during batch change (attemptes:%s failures:%s leftover:%s)"%results)
        return results

    def _is_too_many_failures(self, attempt_count, failure_count):
        if attempt_count <= 2: return False
        return failure_count > int(attempt_count/float(attempt_count)**0.5+1)


    def _batch_change_using_singles(self, change_type, objs):
        objs = list(objs)
        obj = objs.pop(0)
        success = False
        try:
            success = getattr(self, 'single_%s'%change_type)(obj)
        except StoreError:
            pass
        return (success and [obj] or [], not success and [obj] or [], objs)

