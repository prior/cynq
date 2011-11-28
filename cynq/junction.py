from cynq import logging_helper

REMOTE_STORE_FIELD_PROXIES = ['name', 'key']

class Junction(object):
    def __init__(self, local_store, remote_store, cynq_started_at):
        super(Junction, self).__init__()
        self.ls = local_store
        self.rs = remote_store
        self.cynq_started_at = cynq_started_at
        self.rs.junction = self
        self._build_proxies()
        self.fatal_failure = None
        self.log = logging_helper.get_log('cynq.junction.%s' % self.name)

    def _build_proxies(self):
        for field in REMOTE_STORE_FIELD_PROXIES:
            setattr(self, field, getattr(self.rs, field))

    def key_value(self, obj): 
        return obj.get(self.key)

    #def _get_extra_undeleted_locals(self):
        #return (o for o in self.ls.list_ if not o.get('_deleted_at') and not o.get('_error') and o.get(self.key) not in self.ls_hash_)
    #extra_undeleted_locals = property(_get_extra_undeleted_locals)

    def init(self):
        self.rs.clear_stats()

    def local_create(self):
        for robj in self._get_remotes(valid=True, keyed=True, common=False):
            lobj = self.scoped_clone(robj)
            self.log.debug("local create... ( local=%s remote=%s )" % (lobj, robj))
            self.ls.touched_syncables(lobj, self.cynq_started_at)
            self.ls.create(lobj)

    def _local_update_obj(self, lobj, robj):
        diff = self.remote_pushable_merge(lobj, robj)
        self.ls.synced(lobj, self.cynq_started_at)
        if diff:
            self.log.debug("local update... ( delta(old,new)=%s, local=%s )" % (diff, lobj))
            self.ls.touched_syncables(lobj, self.cynq_started_at)
            self.ls.update(lobj)

    def local_reanimate(self):
        for lobj,robj in self._get_locals(valid=True, alive=False, expected=False, keyed=True, common=True, paired=True):
            lobj[self.ls.spec.soft_delete] = None
            self.log.debug("local reanimate... ( local=%s )" % lobj)
            self._local_update_obj(lobj, robj)

    def local_update(self):
        for lobj,robj in self._get_locals(valid=True, alive=True, keyed=True, common=True, paired=True):
            if not self.has_local_changes_since_last_sync(lobj):
                self._local_update_obj(lobj, robj)

    def local_delete(self):
        for lobj in self._get_locals(valid=True, alive=True, expected=True, keyed=True, common=False):
            lobj[self.ls.spec.soft_delete] = self.cynq_started_at
            self.ls.touched_syncables(lobj, self.cynq_started_at)
            self.ls.update(lobj)
            self.log.debug("local delete... ( local=%s )" % lobj)

    def remote_delete(self):
        for lobj,robj in self._get_locals(valid=True, alive=False, expected=True, keyed=True, common=True, paired=True):
            self.log.debug("remote delete... ( remote=%s, local=%s )" % (robj, lobj))
            robj['_source'] = lobj
            self.rs.delete(robj)

    def _remote_create_obj(self, lobj):
        robj = self.remote_pullable_clone(lobj)
        self.log.debug("remote create...(remote=%s, local=%s)" % (robj, lobj))
        robj['_source'] = lobj
        self.rs.create(robj)
        return robj

    def remote_create(self):
        for lobj in self._get_locals(valid=True, expected=False, alive=True, common=False):
            self._remote_create_obj(lobj)

    def _remote_update_obj(self, robj, lobj):
        diff = self.remote_pullable_merge(robj, lobj)
        if diff:
            self.log.debug("remote update... ( delta(old,new)=%s, remote=%s)" % (diff, robj))
            robj['_source'] = lobj
            self.rs.update(robj)
        return robj

    def remote_update(self):
        for lobj,robj in self._get_locals(valid=True, alive=True, keyed=True, common=True, paired=True):
            self._remote_update_obj(robj, lobj)

    def cleanup(self):
        results = self.rs.persist_changes()

        # pull over any updates that happened cuz of remote creates/updates
        for robj in self._get_remotes(valid=True):
            self._local_update_obj(robj['_source'],robj)

        # make sure we mark things that have cynqed as cynqed
        for change_type in results:
            for robj in results[change_type][0]:
                if robj.get('_source') and not self.relevant_object_errors(robj) and not self.releveant_object_errors(robj.get('_source')):
                    self.ls.synced(robj['_source'], self.cynq_started_at)

        # set expectations
        for lobj,robj in self._get_locals(valid=True, keyed=True, common=True, paired=True):
            self.ls.set_expected_remotely(self.name, lobj, True)
        for lobj in self._get_locals(valid=True, common=False):
            self.ls.set_expected_remotely(self.name, lobj, False)

        # force new dates on updated/created stuff
        #self.ls.paint_pending_changes(cynq_started_at, self.rs.)

    def remote_pushable_clone(self, obj):
        return self.rs.pushable_clone(obj)

    def remote_pullable_clone(self, obj):
        return self.rs.pullable_clone(obj)

    def local_pushable_clone(self, obj):
        return self.remote_pullable_clone(obj)

    def local_pullable_clone(self, obj):
        return self.remote_pushable_clone(obj)

    def scoped_clone(self, obj):
        return self.rs.scoped_clone(obj)

    def scoped_diff(self, obj):
        return self.rs.scoped_diff(obj)

    def remote_pushable_merge(self, target, source):
        return self.rs.pushable_merge(target, source)

    def remote_pullable_merge(self, target, source):
        return self.rs.pullable_merge(target, source)

    def relevant_object_errors(self, obj):
        error_keys = set([self.ls.name,self.rs.name]) & set(obj.get('_error',{}))
        return [obj[k] for k in error_keys]

    def is_local_expected_remotely(self, lobj):
        return self.ls.is_expected_remotely(self.name, lobj)

    def has_local_changes_since_last_sync(self, lobj):
        synced_at = lobj.get(self.ls.spec.synced_at)
        syncable_updated_at = lobj.get(self.ls.spec.syncable_updated_at)
        return synced_at and syncable_updated_at and syncable_updated_at > synced_at

    def _get_locals(self, valid=None, alive=None, expected=None, keyed=None, common=None, paired=False):
        arr = []
        for o in self.ls.list_:
            if valid is not None:
                has_errors = self.relevant_object_errors(o)
                if not(valid and not has_errors or not valid and has_errors): continue
            if alive is not None:
                dead = o.get(self.ls.soft_delete)
                if not(alive and not dead or not alive and dead): continue
            if expected is not None:
                has_expectation = self.is_local_expected_remotely(o)
                if not(expected and has_expectation or not expected and not has_expectation): continue
            if keyed is not None:
                key_value = o.get(self.key)
                if not(keyed and key_value is not None or not keyed and key_value is None): continue
            if common is not None:
                intersects = o.get(self.key) in self.remote_hash
                if not(common and intersects or not common and not intersects): continue
            if paired:
                arr.append((o,self.remote_hash.get(o.get(self.key))))
            else:
                arr.append(o)
        return arr

    def _get_remotes(self, valid=None, keyed=None, common=None):
        arr = []
        for o in self.rs.list_:
            if valid is not None:
                has_errors = self.relevant_object_errors(o)
                if not(valid and not has_errors or not valid and has_errors): continue
            if keyed is not None:
                key_value = o.get(self.key)
                if not(keyed and key_value is not None or not keyed and key_value is None): continue
            if common is not None:
                intersects = o.get(self.key) in self.local_hash
                if not(common and intersects or not common and not intersects): continue
            arr.append(o)
        return arr


    def _get_local_hash(self):
        return self.ls.get_hash(self.key)
    local_hash = property(_get_local_hash)

    def _get_remote_hash(self):
        return self.rs.hash_
    remote_hash = property(_get_remote_hash)

