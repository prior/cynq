class ConnectionRemoteCreate(object):
    def __init__(self, connection):
        super(RemoteCreatePhase, self).__init__()
        self.conn = connection
        self.ls = self.conn.local_store
        self.rs = self.conn.remote_store
        self.created_key_values = []
        self.exceptions = []

    def execute(self):
        if not self.ls.createable: return False
        for local in self.ls:
            if not local.deleted_at:
                key_value = self.rs.key_value(local)
                if not key_value or key_value not in self.rs.key_values:
                    if not self.conn.get_remote_expectation(local):
                        try:
                            self._remote_create(local)
                        except(Exception ex):
                            self.exceptions.append(ex)
        return self.created_key_values

    def _remote_create(self, local): # purposefully no try/catch-- want it to bubble up
        new_remote = self.rs.create(local)
        self.rs.merge(target=local, source=new_remote, from_remote=True)
        self.ls.set_remote_expectation(local, self.rs, True)
        key_value = self.rs.key_value(local)
        if not key_value: raise Exception("remote_create yielded no key value!")
        self.log.debug(
            "remote create... ( remote=%s, final_remote=%s, final_local=%s )" % (
                self.rs,
                self.rs.caring_dict(new_remote),
                self.ls.caring_dict(local, self.remote.remote_expectation_attribute)))

