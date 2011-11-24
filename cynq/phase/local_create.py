from cynq.phase.junction_phase import JunctionPhase


#_TODO: deal with possibility of soft or hard deletes in local store-- could make it work with last_updated_syncable_attribute on every junction

#local(remote_id_junction_updated_at)

class LocalCreate(JunctionPhase):
    phase_name = 'local_create'

    def _execute(self, cynq_started_at):
        for (key,remote_obj) in self.rs.hash_.iteritems():
            if not remote_obj.get('_error') and key not in self.jn.local_hash:
                self.ls.create(remote_obj)



        #if not self.ls.createable: return False
        #for remote_obj in self.js
        #for local_obj in self.jn.valid_locals:
            #key_value = self.jn.key_value(local_obj)
            #if not key_value or key_value not in self.rs.hash_:
                #remote_obj = self.rs.copy(local_obj)
                #self.rs.create(remote_obj)
                #self.log.debug("remote create...(local=%s, remote(after)=%s)" % (local_obj, remote_obj))
        #self.rs.persist_changes()
#:

    #def inbound_create_and_update(self):
        #for key in self.remote:
            #remote_obj = self.remote[key]
            #if key in self.local:
                #local_obj = self.local[key]
                #if local_obj.deleted_at:  
                    #if not self._has_remote_expectation(local_obj): #reanimate
                        #self._local_reanimate(local_obj, remote_obj)
                #else: 
                    #if not self._has_local_changed_since_last_sync(local_obj): #update
                        #if not self.remote.readables_seem_equal(local_obj, remote_obj) or not self._has_remote_expectation(local_obj): # only if diff
                            #self._local_update(local_obj, remote_obj)
            #else: #create
                #self._local_create(remote_obj)
