class CynqController(object):
    def __init__(self, fresh, local, snapshot):
        self.fresh = fresh
        self.local = local
        self.snapshot = snapshot

    def cynq(self, initial=True):
        started_at = sanetime()
        local_changeset = self.local.changeset_against(self.snapshot)
        if not initial or not local_changeset: return 0
        remote_changeset = self.remote.changeset_against(self.snapshot)



class MultiCynqController(object):
    def __init__(self, specs):
        self.specs = specs

    def cynq(self):
        total_changes = sum(spec.cynq(True) for spec in self.specs)
        new_changes = 0
        while new_changes:
            total_changes = sum(spec.cynq(False) for spec in self.specs)

    def cynq(self

        junctions = self._build_junctions(self._pre_cynq(cynq_started_at), cynq_started_at)
        if junctions:
            self.local_store.clear_stats()
        changesets = []
        for rs in self.remote_specs:
            try:
                changeset = rs.build_incoming_changeset()
                changeset.merge(rs.build_outgoing_changeset(self.local_spec.store))
                changesets.append(changeset)
            except StandardError:
                rs.fatal_failure = True
        if changesets:
            changeset = changesets[0]
            for i in xrange(1,changesets)
                changeset.merge(changeset[i])
            for rs in self.remote_specs:
                actual_changeset = changeset.copy().filter_and_apply(rs.fresh_store)
                actual_changeset = actualchangeset.filter_and_apply(rs.snapshot_store)

                actual_changeset.filter_and_apply(self.local_spec.store)


        for phase_name in self.phases:
            for j in junctions:
                if not j.fatal_failure:
                    JunctionPhase(j,phase_name,cynq_started_at).execute(cynq_started_at)
        junctions = [j for j in junctions if not j.fatal_failure]
        if junctions:
            self.local_store.persist_changes()
        self._post_cynq(junctions, cynq_started_at)
        self.cynq_started_at = cynq_started_at
        self._report(junctions)

