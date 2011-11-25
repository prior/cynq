from cynq.store.base import BaseStore


class LocalStore(BaseStore):
    FIELD_PROXIES = ('name', 'createable', 'updateable', 'deleteable', 'extras', 'key', 'soft_delete', 'expected_format', 'updated_at_format')

    def __init__(self, local_spec):
        super(LocalStore,self).__init__(local_spec)

    def is_expected_remotely(self, obj, remote_name):
        return obj.get(self.expected_format % {'name':remote_name}, False)

    ## implied attributes = 
    #remote_id_expectation
    #remote_id_syncable_updated_at
    #all of the attributes from all the remotes


    ##
    #def cynq(self):
        #pass


        

