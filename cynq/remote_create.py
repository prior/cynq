import logging_helper
from junction_phase import JunctionPhase

class RemoteCreate(JunctionPhase):
    def __init__(self, junction):
        super(RemoteCreate, self).__init__(junction)
        self.log = logging_helper.get_log('cynq.remote_create.%s' % junction.remote_store.)

    def _execute(self, cynq_started_at):
        raise NotImplementedError()

    def _execute(self, cynq_started_at):
        if not self.rs.createable: return False
        created_key_values = []
        for obj in self.junction.locals_not_in_remote():

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

