import logging_helper

class JunctionPhase(object):
    def __init__(self, junction, phase_type):
        super(JunctionPhase, self).__init__()
        self.junction = junction
        self.ls = junction.local_store
        self.rs = junction.remote_store
        self.phase_type = phase_type
        self.log = logging_helper.get_log('cynq.phase.%s' % phase_type)

    def _pre_phase_hooks(self):
        if not self.ls.pre_cynq_phase(self.phase_type): return False
        if not self.rs.pre_cynq_phase(self.phase_type): return False
        return True
        
    def _post_phase_hooks(self):
        self.ls.post_cynq_phase(self.phase_type)
        self.rs.post_cynq_phase(self.phase_type)
        return True

    def execute(self, cynq_started_at):
        if not self.pre_phase_hooks(cynq_started_at): return False
        try:
            self._execute()
        except JunctionPhaseError as err:
            self.log.error(err)
            self.junction.fatal_failure = err
        self.post_phase_hooks(cynq_started_at)

    def _execute(self, cynq_started_at):
        raise NotImplementedError()


    @classmethod
    def create(kls, phase_type, junction):
        type_to_kls_map = {
                'local_create': LocalCreate
        if phase_type

