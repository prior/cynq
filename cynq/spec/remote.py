from base import Base
from cynq import Cynq

# inherit from this to specify your remotes
class RemoteSpec(Base):
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


class Junction
    def remotes
class RemoteStore(Base):

    def get_all(
