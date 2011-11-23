class LocalSpec(Base):
    def __init__(self, remote_specs):
        DESIGNATIONS = ('createable','updateable','deleteable')
        super(LocalSpec, self).__init__(DESIGNATIONS)

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

    
    # implied attributes = 
    remote_id_expectation
    remote_id_syncable_updated_at
    all of the attributes from all the remotes


    #
    def cynq(self):
        pass

