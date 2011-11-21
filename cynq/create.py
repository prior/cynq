import logging_helper

# gotta deal with partial pools for faster syncing (assuming local is dataset for missing pieces,
#   only works if you can get last changes somehow (can with hubspot, maybe with webex (probably
#   with events, probably not with attendees)

# gotta deal with error scenarios and making sure data stays solid through different error
#   possibilities-- when API is down or just down for a singe object -- and that the cynq's can
#   recover on subsequent cynqa

# gotta be able to easily conditionally hook up remotes and easily conditionally turn on and off
#   different phases (cuz of attendee viewing time window), and cuz don't want to start syncing old
#   attendee data that comes back as zero -- gotta turn off incoming deletes there

# 



phase
  - inbound create
    - for all items not in local pool
        create locally
  - inbound update
  - inbound delete
  - outbound delete
  - outbound update

  - outbound create
    - for each connection
        - for all items not in remote:
            persist changes to remote



        
class RemoteCreate(ObjectChange):
    def __init__(self, connection):
        self.rs = connection.remote_store
        remote_expectation_attribute = connection.remote_expectation_attribute
        self.reset()

    def reset(self):
        self.remote_creates = []

    def queue_changeset(local_object, remote_object):
        for attr in self.rs.writeable_attributes:
            remote_object[attr] = local_object.get(attr)
        remote_object['__remote_create'] = True
        remote_object['']
        self.remote_creates.append(remote_object)

    def persist_changeset(remote):
        self.rs.create(self.remote_creates)  # rs must also set up expetation after successful creation



class RemoteStore():
    def 

    def create(creates):
        for obj in 



        if self.rs.merge(target =

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


        remote_object

        remote_object.
        pass


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

    def is_too_many_failures(attempt_count, failure_count):
        if attempt_count <= 2: return False
        return failure_count > int(failure_count/float(failure_count)**0.5+1)

    def _make_change(self, local_obj, remote_obj):
        self.entity_change_attempts += 1
        try:
            return self._make_change(self, local_obj, remote_obj)
        except ChangeError as err:
            self._error_on_change(err, local_obj):

        # if we get too many errors, just give up
        if len(self.failures) > 3 and len(self.failures)*10 >= create_attempts*10/3

    def _error_on_change(self, err, local_obj):
        """
        stop attempting these changes on many failures, but if mostly success then keep going

        this is judged on a sliding scale that's more tolerant at first but gets very strict very fast, since we
        don't know if an initial failure is the first of many or the only one.
        """
        self.log.error(err)
        self.failures.append(err)
        local_obj.get_default('cynq_error',[]).append(self)
        attempts = self.entity_change_attempts
        if len(attempts > 2:
            if len(self.failures) > int(attempts/float(attempts)**0.5+1):
                raise ConnectionPhaseError("Too many errors, bailing on this connection's phase (%s)" % self)



class ConnectionRemoteCreate(ConnectionPhase):
    def __init__(self, connection):
        super(ConnectionRemoteCreate, self).__init__(connection, 'remote.create')

    def execute(self):
        if not self.ls.createable: return False
        if not self.rs.pre_creates(): return False
        created_key_values = []
        for local_obj in self.ls.all_(deleted_at=None, no_errors_from=self.rs):
            key_value = self.rs.key_value(local_obj)
            if not key_value or key_value not in self.rs.key_values:
                if not self.connection.get_remote_expectation(local_obj):
                    self.make_change(self, local_obj, None)

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



class ConnectionPhaseStats(object):
    def __init__(self, connection, 


class CynqPhase(object):
    def __init__(self, connections, connection_phase_kls):
        super(CynqPhase, self).__init__()
        self.connection_phases = []
        for conn in connections:
            self.connection_phases.append(connection_phase_kls(conn)

    def execute(self, connections_to_ignore=None):
        for connection_phase in self.connection_phases:
            if connection_phase.connection not in (connections_to_ignore or []):
                try:
                    statsconnection_phase.execute()
                except ConnectionPhaseError as err:
                    self.log.error(err, "removing this connection from subsequent cynq phases")
                    connection_phase_errors.append((err,connection_phase.connection))
        if connection_phase_errors:
            raise PhaseError(connection_phase_errors)


class RemoteCreatePhase(object):
    def __init__(self, connections):
        self.connect


class Connection(object):
    def __init__(self, local_store, remote_store):



class Cynq(object):
    CONNECTION_PHASES = [
        LocalCreatePhase,
        LocalUpdatePhase,
        LocalDeletePhase,
        RemoteDeletePhase,
        RemoteUpdatePhase,
        RemoteCreatePhase,
        FinalLocalUpdatePhase ]

    def __init__(self, local_store, remote_stores):
        super(Cynq, self).__init__()
        self.local_store = local_store
        self.remote_stores = remote_stores
        self.connections = 
        self.connection_phases
        for remote_store in self.remote_stores:
            connection = something(local_store, remote_store)
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



