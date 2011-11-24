from cynq.phase.junction_phase import JunctionPhase


#_TODO: deal with possibility of soft or hard deletes in local store-- could make it work with last_updated_syncable_attribute on every junction

#local(remote_id_junction_updated_at)

class RemoteUpdate(JunctionPhase):
    phase_name = 'remote_update'

    def _execute(self, cynq_started_at):
        pass
