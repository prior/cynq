from error import StoreError
import logging_helper

#_TODO: figure out implications of an update of a key attribute-- should we be disallowing such an action

class BaseStore(object):
    def __init__(self, spec):
        super(BaseStore, self).__init__()
        self.spec = spec
        self._list = None
        self._queued = {'creates':[], 'updates':[], 'deletes':[]}
        self.log = logging_helper.get_log('cynq.store.%'%self.spec.id_)

    def _force_get_list(self):
        return self.spec.all_()

    def _get_list(self, supplement=None):
        if self._list is None:
            self._list = self.self._force_get_list()
        return self._list
    list_ = property(_get_list)

    def _force_build_hash(self, key_attr):
        return dict((o[key_attr],o) for o in self.list_ if o.get(key_attr) is not None)

    # playing with objects in that exist in the _list
    def create(self, objs, persist=False): return self.change(objs, 'create', persist)
    def update(self, objs, persist=False): return self.change(objs, 'update', persist)
    def delete(self, objs, persist=False): return self.change(objs, 'delete', persist)
    def change(self, objs, change_type, persist=False):
        self._queued['%ss'%change_type].append(objs)
        getattr(self,'_%sd'%change_type)(objs)
        if persist: self.persist_changes()

    def persist_changes(self):
        for change_type in ['create','update','delete']:
            queue = self._queued['%ss'%change_type]
            if queue:
                getattr(self.spec,'_batch_%s'%change_type)(queue)

    def _created(self, objs): self.list_.extend(objs)
    def _updated(self, objs): pass
    def _deleted(self, objs): [self.list_.remove(o) for o in objs]



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

