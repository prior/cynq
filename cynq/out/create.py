import logging_helper

class Error(Exception):
    """Base class for exceptions in this package"""
    pass

class ConnectionPhaseError(Error):
    """Exception raised when a connection phase fails either partially or fully

    Attributes:
        expr

    """
    def __init__(self, expr, msg):
        self.expr = expr






class ConnectionPhase(object):
    def __init__(self, connection, log_subname=''):
        self.connection = connection
        self.ls = self.connection.local_store
        self.rs = self.connection.remote_store
        self.log = logging_helper.get_log('cynq.conn' + (log_name and ".%s"%log_name))

    def execute(self):
        self.failures = []
        self.entity_change_attempts = 0
        try:
            changed_key_values = self._execute()
        except ConnectionPhaseError as err:
            self.log.error(err)
        return changed_key_values



    def make_change(self, local_obj, remote_obj):
        attempts =
        attempts += 1


class ConnectionRemoteCreate(ConnectionPhase):
    def __init__(self, connection):
        super(ConnectionRemoteCreate, self).__init__(connection, 'remote.create')

    def execute(self):
        if not self.ls.createable: return False
        if not self.rs.pre_creates(): return False
        created_key_values = []
        for local_obj in self.ls.all_undeleted():
            key_value = self.rs.key_value(local_obj)
            if not key_value or key_value not in self.rs.key_values:
                if not self.connection.get_remote_expectation(local_obj):

                    create_attempts += 1
                    try:
                        created_key_values.append(self._remote_create(local))
                    except(Exception ex):
                        self.log.error(ex)
                        self.failures.append(ex)

                    # if we get too many errors, just give up
                    if len(self.failures) > 3 and len(self.failures)*10 >= create_attempts*10/3
        if not self.rs.post_creates(): return False
        return created_key_values

    def _remote_create(self, obj): # purposefully no try/catch-- want it to bubble up
        new_remote = self.rs.create(obj)
        self.rs.merge(target=local, source=new_remote, from_remote=True)
        self.conn.set_remote_expectation(local, True)
        key_value = self.rs.key_value(local)
        if not key_value: raise Exception("remote_create yielded no key value!")
        self.log.debug(
            "remote create... ( remote=%s, final_remote=%s, final_local=%s )" % (
                self.rs,
                self.rs.caring_dict(new_remote),
                self.ls.caring_dict(local, self.remote.remote_expectation_attribute)))
        return key_value



class CynqPhase(object):
    def __init__(self, connections):
        super(CynqPhase, self).__init__()
        self.connections = connections

    def execute(self):
        for conn in self.connections:
            conn_phase = connection_phase_kls(conn)




class RemoteCreatePhase(object):
    def __init__(self, connections):
        self.connect

