from cynq.spec.base import BaseSpec

#important! do not expect these to change during execution!  need to get that in the docs (if you do change them those changes likey won't be honored)
 
# inherit from this to specify your remotes
class RemoteSpec(BaseSpec):

    # overrideable specs
    name = None
    createable = True
    updateable = True
    deleteable = True

    # attributes
    pushed = ()
    pulled = ()
    shared = ()
    key = None
    since = None

    # overrideable methods

    # since is anything-- whatever makes sense to that remote (id if you can be sure nothing changed in previous ids or last_changed_time, etc)
    def all_(self, since=None): raise NotImplementedError() 

    def single_create(self, obj): raise NotImplementedError()
    def single_update(self, obj): raise NotImplementedError()
    def single_delete(self, obj): raise NotImplementedError()

    # batch methods must return tuple of (successes, failures, untried) -- only override if you have legit batch methods, otherwise use single*
    def batch_create(self, objs): raise NotImplementedError()
    def batch_update(self, objs): raise NotImplementedError()
    def batch_delete(self, objs): raise NotImplementedError()

    # pre/post cynq hooks
    def pre_cynq(self, cynq_started_at): return True
    def post_cynq(self, cynq_started_at): return True
    def pre_cynq_phase(self, phase, cynq_started_at): return True
    def post_cynq_phase(self, phase, cynq_started_at): return True


    # private methods
    @classmethod
    def _deduce_all_attrs(kls):
        return kls.pushed + kls.pulled + kls.shared
