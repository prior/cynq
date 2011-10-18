from stores.facet import Facet
from stores.multi_facet import MultiFacet
from connection import Connection
from stores.local_glove import LocalGlove
from sanetime.sanetime import SaneTime

# lots of assumption here:
  # 1) remote store returns no soft_delete items in its list-- not taking that possibility into account right now
  # 2) that you're able to create a full list of your remote entities -- #TODO make it possible to bring in changesets, or only thigns that might've changed since last sync, or partial list, or etc...?
  # 3) .... many others.. #TODO need to expand
class Controller(object):
    def __init__(self, local_store, remote_stores):
        super(Controller,self).__init__()
        self.gloved_local = LocalGlove(local_store)
        self.multifaceted_local = MultiFacet(self.write_cached_local)
        self.connections = []
        synced_at = SaneTime().to_datetime().replace(tzinfo=None)
        for remote in remote_stores:
            faceted_remote = Facet(remote, remote.key_attribute)
            faceted_local = self.multifaceted_local.get_facet(remote.key_attribute)
            conn = Connection(faceted_local, faceted_remote, synced_at)
            self.connections.append(conn)

    def sync(self):
        self._inbound_create()
        self._inbound_update()
        self._inbound_delete()
        self._outbound_delete()
        self._outbound_update()
        self._outbound_create()
        self.write_cached_local.flush()

    def _inbound_create(self):
        for conn in self.connections:
            self.inbound_create()

    def _inbound_update(self):
        for conn in self.connections:
            self.inbound_update()

    def _inbound_delete(self):
        for conn in self.connections:
            self.inbound_delete()

    def _outbound_delete(self):
        for conn in self.connections:
            self.outbound_delete()

    def _outbound_update(self):
        for conn in self.connections:
            self.outbound_update()

    def _outbound_create(self):
        for conn in self.connections:
            self.outbound_create()




