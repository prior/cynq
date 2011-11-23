from base import Base
from cynq import Cynq

class RemoteBase(Base):
    def __init__(self):
        super(RemoteBase, self).__init__()

    def cynq(self, remote_stores):
        return Cynq(self, remote_stores).cynq()


class SpecBase(object):
    def __init__(self):
        super(SpecBase, self).__init__()
    
    # private methods
    def _default_batch_change(self, change_type, objs):
        if not objs: raise ValueError()
        obj = objs.pop(0)
        success = getattr(self, 'single_%s'%change_type)(obj)
        return (success and [obj] or [], not success and [obj] or [], objs)
    

# inherit from this to specify your remotes
class RemoteSpec(SpecBase):
    def __init__(self):
        super(RemoteSpec, self).__init__()

    # overrideable specs
    id = None
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
    def pre_cynq(self, objs): self.stats = Stats(cynq_started_at); return True
    def post_cynq(self, objs): return True
    def pre_cynq_phase(self, phase): return True
    def post_cynq_phase(self, phase): return True

class LocalSpec(SpecBase):
    createable = True
    updateable = True
    deleteable = True
    sinceable = False




class RemoteStore(Base):
    def _create(obj):
        new_obj = self.clone(obj)
        new_obj['_pending_create'] = True
        pool.append(new_obj)
        lenses.

    def _update(source_obj, target_obj=None):
        target_obj = target_obj or 
        
        pool.

    def _all():
        raise NotImplementedError
                
    def _get_pool(self):
        self._pool = self._pool or self._all()



class LocalSpec(SpecBase):

