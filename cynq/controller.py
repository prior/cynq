import logging_helper
from stores.facet import Facet
from stores.multi_facet import MultiFacet
from connection import Connection
from stores.local_glove import LocalGlove

from sanetime import sanetime

# lots of assumption here:
  # 1) remote store returns no soft_delete items in its list-- not taking that possibility into account right now
  # 2) that you're able to create a full list of your remote entities -- #TODO make it possible to bring in changesets, or only thigns that might've changed since last sync, or partial list, or etc...?
  # 3) .... many others.. #TODO need to expand
class Controller(object):
    def __init__(self, local_store, remote_stores):
        super(Controller,self).__init__()
        self.local_store = local_store
        self.gloved_local = LocalGlove(self.local_store)
        self.multifaceted_local = MultiFacet(self.gloved_local)
        self.log = logging_helper.get_log('cynq.controller')
        self.connections = []
        for remote in remote_stores:
            faceted_remote = Facet(remote, remote.key_attribute)
            faceted_local = self.multifaceted_local.get_facet(remote.key_attribute)
            conn = Connection(faceted_local, faceted_remote)
            self.connections.append(conn)

    def sync(self):
        if self.local_store.before_sync_start():
            synced_at = sanetime()
            self.log.debug("Starting sync: %s(%s)" %(repr(synced_at), synced_at.us))
            self._inbound_create_and_update()
            self._inbound_delete(synced_at)
            self._outbound_delete()
            self._outbound_create_and_update()
            self._log_results()
            self.gloved_local.persist(synced_at)
            return self.local_store.after_sync_finish()
        self.log.warn("cynq-ing never attempted cuz before_sync_start returned False")
        return False

    def _inbound_create_and_update(self):
        for conn in self.connections:
            conn.inbound_create_and_update()

    def _inbound_delete(self, synced_at):
        for conn in self.connections:
            conn.inbound_delete(synced_at)

    def _outbound_delete(self):
        for conn in self.connections:
            conn.outbound_delete()

    def _outbound_create_and_update(self):
        for conn in self.connections:
            conn.outbound_create_and_update()

    def _log_results(self):
        for conn in self.connections:
            self.log.info(
                "cynq stats ( remote=%s, local[ reanimates=%s creates=%s updates=%s deletes%s ] remote[ deletes=%s updates=%s creates=%s ] )" % (
                    conn.remote,
                    len(conn.stats['local_reanimates']),
                    len(conn.stats['local_creates']),
                    len(conn.stats['local_updates']),
                    len(conn.stats['local_deletes']),
                    len(conn.stats['remote_deletes']),
                    len(conn.stats['remote_updates']),
                    len(conn.stats['remote_creates'])
                ))
            if conn.stats['local_reanimates']:
                self.log.debug("cynq stats ( remote=%s, local reanimates=%s )" % (conn.remote, conn.stats['local_reanimates']))
            if conn.stats['local_creates']:
                self.log.debug("cynq stats ( remote=%s, local creates=%s )" % (conn.remote, conn.stats['local_creates']))
            if conn.stats['local_updates']:
                self.log.debug("cynq stats ( remote=%s, local updates=%s )" % (conn.remote, conn.stats['local_updates']))
            if conn.stats['local_deletes']:
                self.log.debug("cynq stats ( remote=%s, local deletes=%s )" % (conn.remote, conn.stats['local_deletes']))
            if conn.stats['remote_deletes']:
                self.log.debug("cynq stats ( remote=%s, remote deletes=%s )" % (conn.remote, conn.stats['remote_deletes']))
            if conn.stats['remote_updates']:
                self.log.debug("cynq stats ( remote=%s, remote updates=%s )" % (conn.remote, conn.stats['remote_updates']))
            if conn.stats['remote_creates']:
                self.log.debug("cynq stats ( remote=%s, remote creates=%s )" % (conn.remote, conn.stats['remote_creates']))



