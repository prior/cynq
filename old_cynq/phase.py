import logging_helper

class Phase(object):
    def __init__(self, phase_type, junctions):
        super(Phase, self).__init__()
        self.log = logging_helper.get_log('cynq.phase.%s' % phase_type)
        self.phase_type = phase_type
        self.junctions = junctions
        self.junction_phases = [JunctionPhase.create(phase_type, j) for j in self.junctions]

    #def _pre_phase_hooks(self):
        #if not self.junctions[0].local_store.pre_cynq_phase(self.phase_type): return False
        #return True
        
    #def _post_phase_hooks(self):
        #self.junctions[0].local_store.post_cynq_phase(self.phase_type)

    def execute(self, cynq_started_at):
        if not self.junctions: return False
        #if not self.pre_phase_hooks(cynq_started_at): return False
        for jp in self.junction_phases:
            try:
                jp.execute()
            except JunctionPhaseError as err:
                self.log.error(err)
                jp.junction.fatal_failure = err
        #if not self.pre_phase_hooks(cynq_started_at): return False

