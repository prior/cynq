from cynq.error import StoreError
import cynq.logging_helper

#TODO: test cached levels

class BaseStore(object):
    def __init__(self, spec):
        super(BaseStore, self).__init__()
        self.spec = spec
        self._list = None
        self._hashes = {}
        self._queued = {'creates':[], 'updates':[], 'deletes':[]}
        self.log = logging_helper.get_log('cynq.store.%'%self.spec.id_)

    def _force_get_list(self):
        return self.spec.all_()

    def _get_list(self):
        if self._list is None:
            self._list = self.self._force_get_list()
        return self._list
    list_ = property(_get_list)

    def _force_build_hash(self, key_attr):
        return dict((o[key_attr],o) for o in self.list_ if o.get(key_attr) is not None)

    def get_hash(self, key_attr):
        if self._hashes.get(key_attr) is None:
            self._hashes[key_attr] = self._force_build_hash(key_attr)
        return self._hashes[key_attr]


    # playing with objects in that exist in the _list
    def create(self, obj): return self.change(obj, 'create')
    def update(self, obj): return self.change(obj, 'update')
    def delete(self, obj): return self.change(obj, 'delete')
    def change(self, obj, change_type):
        self._queued['%ss'%change_type].append(obj)
        getattr(self,'_%sd'%change_type)(obj)

    def persist_changes(self):
        for change_type in ['create','update','delete']:
            queue = self._queued['%ss'%change_type]
            if queue:
                getattr(self.spec,'batch_%s'%change_type)(queue)
                queue.clear()

    def _created(self, objs):
        self.list_.extend(objs)
        for key in self._hashes:
            for obj in objs:
                hash_ = self._hashes[key]
                key_value = obj.get(key)
                if key_value is not None:
                    if key_value in hash_: raise Error("key already exists!")  #_TODO: embellish
                    if obj in hash_.values(): raise Error("obj already in hash!")  #_TODO: embellish
                    hash_[key_value] = obj

#_TODO: figure out implications of an update of a key attribute-- should we be disallowing such an action
    def _updated(self, objs):
        for key in self._hashes:
            for obj in objs:
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

    def _deleted(self, objs): 
        [self.list_.remove(o) for o in objs]
        for key in self._hashes:
            for obj in objs:
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
            obj['_error'] = err
            self.log.error(err)
            raise StoreError(self, err)

    #proxy spec functions with proper exception handling
    def batch_create(self, objs): return self._batch_change(self, 'create', objs)
    def batch_update(self, objs): return self._batch_change(self, 'update', objs)
    def batch_delete(self, objs): return self._batch_change(self, 'delete', objs)
    def _batch_change(self, change_type, objs):
        results = ([],[],objs)
        while len(results[2]):
            results = getattr(self.spec, 'batch_%s'%change_type)(objs)
            for obj in results[1]: obj.setdefault('_error',True)
            if self._is_too_many_failures(len(results[0]) + len(results[1]), len(results[1])):
                raise StoreError("Too many failures during batch change (attemptes:%s failures:%s leftover:%s)"%results)
        return results[0] + results[1]

    def _is_too_many_failures(self, attempt_count, failure_count):
        if attempt_count <= 2: return False
        return failure_count > int(attempt_count/float(attempt_count)**0.5+1)

