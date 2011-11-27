from cynq import logging_helper

class JunctionPhase(object):
    def __init__(self, junction, phase_name):
        super(JunctionPhase, self).__init__()
        self.jn = junction
        self.phase_name = phase_name
        self.ls = junction.ls
        self.rs = junction.rs
        self.log = logging_helper.get_log('cynq.%s' % self.phase_name)

    def _pre_phase_hooks(self, cynq_started_at):
        if not self.ls.spec.pre_cynq_phase(self.phase_name, self.jn.name, cynq_started_at): return False
        if not self.rs.spec.pre_cynq_phase(self.phase_name, cynq_started_at): return False
        return True
        
    def _post_phase_hooks(self, cynq_started_at):
        self.ls.spec.post_cynq_phase(self.phase_name, self.jn.name, cynq_started_at)
        self.rs.spec.post_cynq_phase(self.phase_name, cynq_started_at)

    def execute(self, cynq_started_at):
        if self.jn.fatal_failure: return False
        if not self._pre_phase_hooks(cynq_started_at): return False
        try:
            self._execute(cynq_started_at)
        except StandardError as err:
            self.log.error(err)
            self.jn.fatal_failure = err
            raise  #TODO: just temporary
        self._post_phase_hooks(cynq_started_at)

    def _execute(self, cynq_started_at):
        return getattr(self.jn, self.phase_name)(cynq_started_at)

