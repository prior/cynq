import copy
import logging_helper
from error import StoreError

class Base(object):
    def __init__(self, designations):
        super(Base, self).__init__()
        for designation in designations:  # bring designations into instance fields
            setattr(self, designation, getattr(self.__class__, designation))
        self.log = logging_helper.get_name('cynq.spec.%s', self.id_)
    
    #wrapping up provided functions with proper exception handling
    def _all(self, since=None):
        try: self._all(since=since)
        except StandardError as err: raise StoreError(self, err)

    def _single_create(self, obj): return self._single_change('create', obj)
    def _single_update(self, obj): return self._single_change('update', obj)
    def _single_delete(self, obj): return self._single_change('delete', obj)
    def _single_change(self, change_type, obj):
        try: 
            return getattr(self, 'single_%s'%change_type)(obj)
        except StandardError as err: 
            self._mark_error_on_object(obj, err)
            raise StoreError(self, err)

    #wrapping up provided functions with proper exception handling
    def _batch_create(self, objs): return self._batch_change(self, 'create', objs)
    def _batch_update(self, objs): return self._batch_change(self, 'update', objs)
    def _batch_delete(self, objs): return self._batch_change(self, 'delete', objs)
    def _batch_change(self, change_type, objs):
        results = ([],[],objs)
        while len(results[2]):
            results = getattr(self, 'batch_%s'%change_type)(objs)
            for o in results[1]: self._mark_error_on_object(o, True)
            if self._is_too_many_failures(len(results[0]) + len(results[1]), len(results[1])):
                raise StoreError("Too many failures during batch change (attemptes:%s failures:%s leftover:%s)"%results)
        return results[0] + results[1]


    # private methods
    def _single_batch_change(self, change_type, objs):
        if not objs: raise ValueError()
        obj = objs.pop(0)
        success = False
        try:
            success = getattr(self, '_single_%s'%change_type)(obj)
        except StoreError as err:
            self.log.error(err)
        return (success and [obj] or [], not success and [obj] or [], objs)

    def _mark_error_on_object(self, obj, err):
        obj._error = getattr(obj,'_error', {})
        obj._error[self.id_] = err

    def _is_too_many_failures(self, attempt_count, failure_count):
        if attempt_count <= 2: return False
        return failure_count > int(attempt_count/float(attempt_count)**0.5+1)




class TestMemorySpec(Base):
    def __init__(self, seeds=None, key=None, push_gen=None):
        super(TestMemorySpec, self).__init__()
        self.hash_ = self.hashify_list(seeds or [])
        self.push_gen = push_gen
        self.crud_stats = (0,0,0,0)
        self.hash_ = dict((o.get(self.key), o) for o in self.all_())

    def all_(self):
        self._pre(read=True)
        list_ = self.hash_.values()
        self._pre(read=True)
        return list_

    def single_create(self, obj):
        self._pre(create=obj)
        for attr in self.pushed:
            obj[attr] = self.push_gen(attr)
        self.hash_[obj[self.key]] = obj
        self._post(create=obj)
        return obj

    def single_update(self, obj):
        self._pre(update=obj)
        for attr in self.pushed:
            if obj.get(attr) is None:
                obj[attr] = self.push_gen(attr)
        self.hash_[obj[self.key]] = obj
        self._post(update=obj)
        return obj

    def single_delete(self, obj):
        self._pre(delete=obj)
        del self.hash_[obj[self.key]]
        self._post(delete=obj)

    def _pre(self, read=False, create=False, update=False, delete=False):
        for change_type in ['create', 'update', 'delete']:
            if locals().get(change_type):
                list_ = getattr(self, "%ss_before"%change_type, [])
                list_.append(copy(locals().get(change_type)))
                setattr(self, "%ss_before"%change_type, list_)

    def _post(self, read=False, create=False, update=False, delete=False):
        self.crud_stats = (
            self.crud_stats[0] + (read and 1 or 0),
            self.crud_stats[1] + (create and 1 or 0),
            self.crud_stats[2] + (update and 1 or 0),
            self.crud_stats[3] + (delete and 1 or 0) )
        for change_type in ['create', 'update', 'delete']:
            if locals().get(change_type):
                list_ = getattr(self, "%ss_after"%change_type, [])
                list_.append(copy(locals().get(change_type)))
                setattr(self, "%ss_after"%change_type, list_)




# inherit from this to specify your remotes
class RemoteSpec(Base):
    def __init__(self):
        DESIGNATIONS = ['id_','pushed','pulled','shared','key','since','createable','updateable','deleteable','sinceable']
        super(RemoteSpec, self).__init__(DESIGNATIONS)

    # overrideable specs
    id_ = None
    pushed = []
    pulled = []
    shared = []
    key = None
    since = None

    createable = True
    updateable = True
    deleteable = True
    sinceable = False

    # overrideable methods

    # since is anything-- whatever makes sense to that remote (id or time, etc)
    def all_(self, since=None): raise NotImplementedError() 

    def single_create(self, obj): raise NotImplementedError()
    def single_update(self, obj): raise NotImplementedError()
    def single_delete(self, obj): raise NotImplementedError()

    # batch methods must return tuple of (successes, failures, untried)
    def batch_create(self, objs): return self.default_batch_change('create', objs)
    def batch_update(self, objs): return self.default_batch_change('update', objs)
    def batch_delete(self, objs): return self.default_batch_change('delete', objs)

    # pre/post cynq hooks
    def pre_cynq(self, cynq_started_at): return True
    def post_cynq(self, cynq_started_at): return True
    def pre_cynq_phase(self, phase, cynq_started_at): return True
    def post_cynq_phase(self, phase, cynq_started_at): return True


    def _get_writeables(self):
        property(


class LocalSpec(Base):
    def __init__(self, remote_specs):
        DESIGNATIONS = ['createable','updateable','deleteable']
        super(LocalSpec, self).__init__(DESIGNATIONS)
        self.remotes = dict((rs.id_,rs) for rs in remote_specs)

    # overrideable specs
    createable = True
    updateable = True
    deleteable = True

    # overrideable methods

    # since is anything-- whatever makes sense to that remote (id or time, etc)
    def all_(self): raise NotImplementedError() 

    def single_create(self, obj): raise NotImplementedError()
    def single_update(self, obj): raise NotImplementedError()
    def single_delete(self, obj): raise NotImplementedError()

    # batch methods must return tuple of (successes, failures, untried)
    def batch_create(self, objs): return self.default_batch_change('create', objs)
    def batch_update(self, objs): return self.default_batch_change('update', objs)
    def batch_delete(self, objs): return self.default_batch_change('delete', objs)

    # pre/post cynq hooks
    def pre_cynq(self, cynq_started_at): return True
    def post_cynq(self, cynq_started_at): return True
    def pre_cynq_phase(self, phase, remote_id, cynq_started_at): return True
    def post_cynq_phase(self, phase, remote_id, cynq_started_at): return True

    
    #
    def cynq(self):
        pass

    def is_writeably_different(self, remote_id, local_obj, remote_obj):
        any(self.

