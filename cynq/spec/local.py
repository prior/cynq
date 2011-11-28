from cynq.spec.base import BaseSpec

class LocalSpec(BaseSpec):

    # overrideable specs
    local_store = None # store kls 

    # overrideable methods
    # pre/post cynq hooks
    def pre_cynq(self, cynq_started_at): return True
    def post_cynq(self, cynq_started_at): return True
    def pre_cynq_phase(self, phase, cynq_started_at): return True
    def post_cynq_phase(self, phase, cynq_started_at): return True

    def createable(self, cynq_started_at): return True
    def updateable(self, cynq_started_at): return True
    def deleteable(self, cynq_started_at): return True


