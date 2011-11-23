from cynq.phase.junction_phase import JunctionPhase


#_TODO: deal with possibility of soft or hard deletes in local store-- could make it work with last_updated_syncable_attribute on every junction

#local(remote_id_junction_updated_at)

class RemoteCreate(JunctionPhase):
    phase_name = 'remote_create'

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

