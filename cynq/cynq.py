import logging_helper
from sanetime import sanetime
from junction import Junction
from store import LocalStore, RemoteStore
from phase import LocalCreate, LocalUpdate, LocalDelete, RemoteDelete, RemoteUpdate, RemoteCreate, LimitedLocalUpdate


PHASES = [ LocalCreate, LocalUpdate, LocalDelete, RemoteDelete, RemoteUpdate, RemoteCreate, LimitedLocalUpdate ]

class Cynq(object):
    def __init__(self, local_spec, remote_specs):
        super(Cynq, self).__init__()
        self.log = logging_helper.get_log('cynq')
        self.local_store = LocalStore(local_spec)
        self.remote_stores = [RemoteStore(rs) for rs in remote_specs]
        self.phases = list(PHASES)

    def _build_junctions(self, remote_stores):
        junctions = []
        for remote_store in remote_stores:
            junctions.append(Junction(self.local_store, remote_store))
        return junctions

    def _pre_cynq(self, cynq_started_at):
        if not self.local_store.pre_cynq():
            self.log.warn("pre-cynq hook on local store prevented cynq execution %s" % self.local_store)
            return False
        remote_stores_to_sync = []
        for rs in self.remote_stores:
            if rs.pre_cynq():
                remote_stores_to_sync.append(rs)
            else:
                self.log.warn("pre-cynq hook on remote store prevented it from being included in cynq (rs:%s)" % rs)
        if not remote_stores_to_sync:
            self.log.warn("all remote stores were excluded by pre-cynq hooks, so no cynq happening")
            return False
        return remote_stores_to_sync

    def _post_cynq(self, junctions, cynq_started_at):
        self.local_store.post_cynq(cynq_started_at)
        for j in junctions:
            j.remote_store.post_cynq(cynq_started_at)

    def cynq(self):
        cynq_started_at = sanetime()
        junctions = self.build_junctions(self._pre_cynq(cynq_started_at))
        for phase_kls in self.phases:
            for j in junctions:
                if not j.fatal_failure:
                    phase_kls(j).execute(cynq_started_at)
        junctions = [j for j in junctions if not j.fatal_failure]
        if junctions:
            self.local_store.persist_changes(cynq_started_at)
        self._post_cynq(junctions, cynq_started_at)
        self._report(junctions)

    def _report(self, junctions):
        pass

        #self.log.debug("started cynq: %s(%s)" %(repr(sync_started_at), sync_started_at.us))
        #self._log_results()
            #self._log_results()
            #self.gloved_local.persist(synced_at)
            #return self.local_store.after_sync_finish(self.total_changes > 0)
        #self.log.warn("cynq-ing never attempted cuz before_sync_start returned False")
        #return False

