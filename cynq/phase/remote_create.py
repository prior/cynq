import logging_helper


class JunctionPhase(object):
    def __init__(self, junction, phase_type):
        super(Phase, self).__init__()
        self.junction = junction
        self.ls = junction.local_store
        self.rs = junction.remote_store
        self.phase_type = phase_type
        self.log = logging_helper.get_log('cynq.%s.%s' % phase_type)

    def _pre_phase_hooks(self, cynq_started_at):
        if not self.ls.spec.pre_cynq_phase(self.phase_type, self.junction.id_, cynq_started_at): return False
        if not self.rs.spec.pre_cynq_phase(self.phase_type, cynq_started_at): return False
        return True
        
    def _post_phase_hooks(self, cynq_started_at):
        self.ls.spec.post_cynq_phase(self.phase_type, self.junction.id_, cynq_started_at)
        self.rs.spec.post_cynq_phase(self.phase_type, cynq_started_at)

    def execute(self, cynq_started_at):
        if not self.junction.active: return False
        if not self._pre_phase_hooks(cynq_started_at): return False
        try:
            self._execute()
        except StandardError as err:
            self.log.error(err)
            self.junction.deactivate()
        self._post_phase_hooks(cynq_started_at)

    def _execute(self, cynq_started_at):
        raise NotImplementedError()


class RemoteCreate(JunctionPhase):
    def __init__(self, junction):
        super(RemoteCreate, self).__init__(junction, 'remote_create')

    def _execute(self, cynq_started_at):
        if not self.rs.spec.createable: return False

        remote_creates = []
        for obj in self.junction.ls.list_:
            if not obj.get('_error') and not obj.get('_deleted_at'):
                key_value = self.junction.key_value(obj)
                if not key_value or key_value not in self.rs.hash_:
                    remote_creates.append(self.rs.writeably_clone(obj))
        self.rs.create(remote_creates, persist=True)

    def _remote_create(self, obj): # purposefully no try/catch-- want it to bubble up
        new_remote = self.rs.create(obj)
        self.rs.merge(target=local, source=new_remote, from_remote=True)
        self.conn.set_remote_expectation(local, True)
        key_value = self.rs.key_value(local)
        if not key_value: raise Exception("remote_create yielded no key value!")
        self.log.debug(
            "remote create... ( remote=%s, final_remote=%s, final_local=%s )" % (
                self.rs,
                self.rs.caring_dict(new_remote),
                self.ls.caring_dict(local, self.remote.remote_expectation_attribute)))
        return key_value

