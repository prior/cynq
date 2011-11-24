from cynq.phase.junction_phase import JunctionPhase


#_TODO: deal with possibility of soft or hard deletes in local store-- could make it work with last_updated_syncable_attribute on every junction

#local(remote_id_junction_updated_at)

class RemoteCreate(JunctionPhase):
    phase_name = 'remote_create'

    def _execute(self, cynq_started_at):
        if not self.rs.createable: return False
        for local_obj in self.jn.valid_locals:
            key_value = self.jn.key_value(local_obj)
            if not key_value or key_value not in self.rs.hash_:

                remote_obj = self.rs.copy(local_obj)

                self.jn.local_update(local_obj, self.rs.create(local_obj))

                self.jn.set_expected_remote()

                local_obj.merge(self.rs.create(local_obj))

                self.log.debug("remote create...(local=%s, remote(after)=%s)" % (local_obj, remote_obj))


        self.rs.persist_changes()

