import logging_helper
from phases import LocalCreatePhase
from phases import LocalUpdatePhase
from phases import LocalDeletePhase
from phases import RemoteDeletePhase
from phases import RemoteUpdatePhase
from phases import RemoteCreatePhase
from phases import FinalLocalUpdatePhase
from connection import Connection



CONNECTION_PHASES = [
    LocalCreatePhase,
    LocalUpdatePhase,
    LocalDeletePhase,
    RemoteDeletePhase,
    RemoteUpdatePhase,
    RemoteCreatePhase,
    FinalLocalUpdatePhase ]

class Cynq(object):
    def __init__(self, local_store, remote_stores):
        super(Cynq, self).__init__()
        self.log = logging_helper.get_log('cynq')
        self.local_store = local_store
        self.remote_stores = remote_stores

        self.connections = []
        for remote_store in self.remote_stores:
            self.connections.append(Connection(local_store, remote_store))

        self.connections = []
        for connection 
            self.connection_phases = (CynqPhase(p) for p in CONNECTION_PHASES)

    def pre_cynq_hooks()
        if not self.local_store.pre_cynq():
            self.log.warn("pre-cynq hook on local store prevented cynq execution")
            return False
        self.remote_stores_to_sync = []
        for rs in self.remote_stores:
            if rs.pre_cynq():
                self.remote_stores_to_sync.append(rs)
            else:
                self.log.warn("pre-cynq hook on remote store prevented it from being included in cynq (rs:%s)" % rs)
        if not remote_stores_to_sync:
            self.log.warn("all remote stores were excluded by pre-cynq hooks, so not cynq")
            return False
        return self.remote_stores_to_sync

    def post_cynq_hooks()
        self.local_store.post_cynq():
        for rs in self.remote_storesto_sync:
            if rs.post_cynq():
    
    def cynq(self):
        synced_at = sanetime()
        if not pre_cynq_hooks(sync_started_at):
            return False
        for phase in self.phases:
            total_changes += phase.execute(sync_started_at)
        if not post_phases_hooks():
            return False
        self.local_store.persist(sync_started_at)
        self.post_cynq_hooks(sync_started_at, total_changes)

        self.log.debug("started cynq: %s(%s)" %(repr(sync_started_at), sync_started_at.us))
        self._log_results()
            self._log_results()
            self.gloved_local.persist(synced_at)
            return self.local_store.after_sync_finish(self.total_changes > 0)
        self.log.warn("cynq-ing never attempted cuz before_sync_start returned False")
        return False



