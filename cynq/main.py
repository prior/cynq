Spec
  pushed
  pulled
  shared
  (attrs)
  key

Store
  - spec
  all_() cache it


Local
    -present_key1 (store)
       -change_set_from (rmeote1_past)
    -present_key2 (store)
       -change_set_from (rmeote2_past)

Remote
    -past (store)
    -present (store)
       -change_set_from (remote_past)

for rs in remote_stores:
    get_change_set1
    get_change_set2
    rs.merged_changeset = merge_changesets

iteratively merge across remote stores

for rs in remote_stores:
    actual_changes_happened = rs.present_store.apply_changeset()
    actual_changes_happened = rs.past_store.apply_changeset (also updating synced_at timestamps)
    local_store.apply_changeset


for rs in remote_stores:
    rs.merged_changeset = rs.merge


class Controller(object):
    def __init__(self, local_spec, remote_specs):
        super(Controller,self).__init__()
        self.local_spec = local_spec
        self.remote_specs = remote_specs

    def cynq(self):
        started_at = sanetime()
        for stale,fresh in self.remote_specs.stores:
            ChangeSet(stale.key,


    def _post_cynq(self, junctions, cynq_started_at):
        self.local_store.spec.post_cynq(cynq_started_at)
        for j in junctions:
            j.rs.spec.post_cynq(cynq_started_at)

    def cynq(self):
        cynq_started_at = sanetime()
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

    def _pre_cynq(self, started_at):
        if not self.local.spec.pre_cynq(started_at):
            self.log.warn("pre-cynq hook on local store prevented cynq execution %s" % self.local_store)
            return False
        remote_stores_to_sync = []
        for rs in self.remote_stores:
            if rs.spec.pre_cynq(cynq_started_at):
                remote_stores_to_sync.append(rs)
            else:
                self.log.warn("pre-cynq hook on remote store prevented it from being included in cynq (rs:%s)" % rs)
        if not remote_stores_to_sync:
            self.log.warn("all remote stores were excluded by pre-cynq hooks, so no cynq happening")
            return False
        return remote_stores_to_sync


    




