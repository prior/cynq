import logging_helper

class Junction(object):
    def __init__(self, local_store, remote_store):
        super(Junction, self).__init__()
        self.ls = local_store
        self.rs = remote_store
        self.key = self.rs.spec.key
        self.id_= self.rs.spec.id_
        self.active = True
        self.log = logging_helper.get_log('cynq.junction.%s' % self.rs.spec.id_)

    def deactivate(self): 
        self.active = False

    def key_value(self, obj): 
        return obj.get(self.key)

    def _get_extra_undeleted_locals(self):
        return (o for o in self.ls.list_ if not o.get('_deleted_at') and not o.get('_error') and o.get(self.key) not in self.ls_hash_)
    extra_undeleted_locals = property(_get_extra_undeleted_locals)



