from changeset import ChangeSet

class Arm(object):

    # private methods
    def __init__(self, api_store, local_store, snapshot_store):
        super(Arm,self).__init__()
        self.controller = None  # will get set by owning controller on cynq setup
        self.spec = api_store.spec
        self.stores = (api_store, local_store, snapshot_store)
        self.api, self.local, self.snapshot = self.stores
        self.api.set_arm(self,'api')
        self.local.set_arm(self,'local')
        self.snapshot.set_arm(self,'snapshot')

    def _pre_cynq(self):
        return all(store._pre_cynq() for store in self.stores)

    def _post_cynq(self):
        return all(store._post_cynq() for store in self.stores)

    def _cynq_api(self):
        print "before_api"
        print self.api.ddata
        print self.local.ddata
        print self.snapshot.ddata
        outgoing_changeset = ChangeSet(self.spec).build(self.local, self.snapshot)
        incoming_changeset = ChangeSet(self.spec).build(self.api, self.snapshot)
        self.api.apply_changeset(outgoing_changeset.subtract(incoming_changeset))
        print "after_api"
        print self.api.ddata
        print self.local.ddata
        print self.snapshot.ddata

    def _cynq_local(self):
        print "before_local"
        print self.api.ddata
        print self.local.ddata
        print self.snapshot.ddata
        outgoing_changeset = ChangeSet(self.spec).build(self.local, self.snapshot)
        incoming_changeset = ChangeSet(self.spec).build(self.api, self.snapshot) 
        outgoing_changeset = incoming_changeset.subtract(outgoing_changeset)
        print outgoing_changeset.creates
        self.local.apply_changeset(outgoing_changeset)
        print "after_local"
        print self.api.ddata
        print self.local.ddata
        print self.snapshot.ddata

    def _cynq_snapshot(self):
        print "before_cnapsot"
        print self.api.ddata
        print self.local.ddata
        print self.snapshot.ddata
        incoming_changeset = ChangeSet(self.spec).build(self.api, self.snapshot) 
        self.snapshot.apply_changeset(incoming_changeset)
        print "after_snapshot"
        print self.api.ddata
        print self.local.ddata
        print self.snapshot.ddata

