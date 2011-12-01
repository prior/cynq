from . import ChangeSet

class Arm(object):

    # private methods
    def __init__(self, spec, api_store, local_store, snapshot_store):
        super(Arm,self).__init__()
        self.controller = None  # will get set by owning controller on cynq setup
        self.spec = spec
        self.api = api_store.with_arm(self, 'api')
        self.local = local_store.with_arm(self, 'local')
        self.snapshot = snapshot_store.with_arm(self, 'snapshot')
        self.stores = (self.api, self.local, self.snapshot)

    def _pre_cynq(self):
        return all(store._pre_cynq() for store in (self.api, self.local, self.snapshot))

    def _post_cynq(self):
        return all(store._post_cynq() for store in (self.api, self.local, self.snapshot))

    def _cynq_api(self):
        outgoing_changeset = ChangeSet(self.spec).build(self.local, self.snapshot, self.spec.rpushed)
        incoming_changeset = ChangeSet(self.spec).build(self.api, self.snapshot)
        self.api.apply_changeset(outgoing_changeset.subtract(incoming_changeset))

    def _cynq_local(self):
        outgoing_changeset = ChangeSet(self.spec).build(self.local, self.snapshot)
        incoming_changeset = ChangeSet(self.spec).build(self.api, self.snapshot, self.spec.rpulled) 
        self.local.apply_changeset(incoming_changeset.subtract(outgoing_changeset))

    def _cynq_snapshot(self):
        incoming_changeset = ChangeSet(self.spec).build(self.api, self.snapshot) 
        self.snapshot.apply_changeset(incoming_changeset)

