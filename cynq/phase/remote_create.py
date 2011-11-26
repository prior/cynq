from cynq.phase.junction_phase import JunctionPhase


#_TODO: deal with possibility of soft or hard deletes in local store-- could make it work with last_updated_syncable_attribute on every junction

#local(remote_id_junction_updated_at)

class RemoteCreate(JunctionPhase):
    phase_name = 'remote_create'

    def _execute(self, cynq_started_at):
        if not self.rs.createable: return False
        for lobj in self.jn.unexpected_valid_living_locals:
            key_value = self.jn.key_value(lobj)
            if key_value is None or key_value not in self.rs.hash_:
                robj = self.jn.remote_pullable_clone(lobj)
                pairings.append((lobj,robj))
                self.log.debug("remote create...(local=%s, remote(before)=%s)" % (lobj, robj))
        self.rs.persist_changes()
        for lobj,robj in pairings:
            self.jn.remote_pushable_merge(robj, lobj)
            self.log.debug("remote create...(local=%s, remote(after)=%s)" % (lobj, robj))


