from cynq.error import Error,StoreError
from cynq import logging_helper
from traceback import format_exc

#TODO: factor out spec and arm from each other (spec can be owned by stores, and arms own stores)

class BaseStore(object):
    # all the methods available to override (but should not be called directly by you ever!)
    def _all(self): raise NotImplementedError()
    
    # you can choose to implement just the bulk ones or just the single ones-- not really a need to implement both
    def _bulk_create(self, dobjs): raise NotImplementedError() # return dobj,obj tuples (obj is None on failure)    exceptions unnecessary(will get picked up in failures) 
    def _bulk_update(self, update_tuples): raise NotImplementedError()  # return key,obj,djchanges tuples (obj is None on failure) (update_tuple=(key, dchanges))    exceptions unnecessary(will get picked up in failures) 
    def _bulk_delete(self, keys): raise NotImplementedError() # return key,obj tuples (obj is None on failure)    exceptions unnecessary(will get picked up in failures) 

    def _single_create(self, dobj): raise NotImplementedError()  # returns new obj   throws exception on error
    def _single_update(self, key, dchanges): raise NotImplementedError()  # returns obj with changes  throws excption on error
    def _single_delete(self, key): raise NotImplementedError()  # returns obj if   throws exception on error

    def _pre_cynq(self): return True
    def _post_cynq(self): return True

    def _createable(self): return True
    def _updateable(self): return True
    def _deleteable(self): return True


    # public methods
    def bulk_create(self, dobjs):
        if not self._createable(): return # avoid error reporting since this is on purpose
        print "BULK_CREATE (LEN=%s)" %len(dobjs)
        print "dobjs = %s" % dobjs
        print "ddata = %s" % self.ddata
        try:
            for dobj,obj in self._bulk_create(dobjs):
                if obj: self._single_created(obj, dobj)
                else: self._single_create_fail(dobj)
        except NotImplementedError:
            print "NOT IMPLEMENTED -- DROPPING TO SINGLE CREATE"
            print "ddata = %s" % self.ddata
            for dobj in dobjs:
                self.single_create(dobj)

    def single_create(self, dobj):
        print "SINGLE CREATE  ddata=%s"% self.ddata
        try:
            print "BEFORE _SINGLE_CREATE ddata=%s" % self.ddata
            obj = self._single_create(dobj)
            print "BETWEEn _SINGLE_CREATE ddata=%s" % self.ddata
            self._single_created(obj, dobj)
            print "AFTER _SINGLE_CREATE ddata=%s" % self.ddata
        except NotImplementedError:
            raise Error("You need to implement either the _single_create or the _bulk_create")
        except StandardError as err:
            self._single_create_fail(dobj, err)


    def bulk_update(self, tuples):
        if not self._updateable(): return  # avoid error reporting since this is on purpose
        try:
            for key,obj,dchanges in self._bulk_update(tuples):
                if obj: self._single_updated(key, dchanges)
                else: self._single_update_fail(key, dchanges)
        except NotImplementedError:
            for key,dchanges in tuples:
                self.single_update(key, dchanges)

    def single_update(self, key, dchanges):
        try:
            self._single_update(key, dchanges)
            self._single_updated(key, dchanges)
        except NotImplementedError:
            raise Error("You need to implement either the _single_update or the _bulk_update")
        except StandardError as err:
            self._single_update_fail(key, dchanges, err)

    def bulk_delete(self, keys):
        if not self._deleteable(): return # avoid error reporting since this is on purpose
        try:
            for key,obj in self._bulk_delete(keys):
                if obj: self._single_deleted(key)
                else: self._single_delete_fail(key)
        except NotImplementedError:
            for key in keys:
                self.single_delete(key)

    def single_delete(self, key):
        try:
            self._single_delete(key)
            self._single_deleted(key)
        except NotImplementedError:
            raise Error("You need to implement either the _single_delete or the _bulk_delete")
        except StandardError as err:
            self._single_delete_fail(key, err)

    def apply_changeset(self, changeset):
        self.bulk_create(changeset.creates.values())
        self.bulk_update(changeset.updates.iteritems())
        self.bulk_delete(changeset.deletes)
        self.bulk_create(changeset.keyless_creates.values())

    def generate_update_trigger(self, obj):
        def trigger(new_key_value):
            setattr(obj, self.key, new_key_value)
            if self.bulk_update((obj, {self.key : new_key_value})):
                self.hash_[new_key_value] = obj
        return trigger


    #private methods
    def __init__(self, spec):
        super(BaseStore, self).__init__()
        self.arm, self.type_ = None,None # will get set by owning arm during cynq setup
        self.spec = spec
        self.key = spec.key
        self._clear_cache()
        self.changes = [0,0,0,0,0,0] #success/fails for create/update/delete

    def _single_created(self, obj, dobj):
        print "1 _SINGLE_CREATE ddata=%s" % self.ddata
        self.changes[0] += 1
        print "2 _SINGLE_CREATE ddata=%s" % self.ddata
        self.log.debug('create | key=%s | dobj=%s | obj=%s' % (getattr(obj,self.key), dobj, obj))
        print "3 _SINGLE_CREATE ddata=%s" % self.ddata
        print id(self._list)
        print id(self.data)
        self.list_.append(obj)
        print "4 _SINGLE_CREATE ddata=%s" % self.ddata
        self.hash_[getattr(obj,self.key)] = obj
        print "5 _SINGLE_CREATE ddata=%s" % self.ddata
        if dobj.get('_keyless_update_trigger'): dobj['_keyless_update_trigger'](getattr(obj, self.key))
        print "6 _SINGLE_CREATE ddata=%s" % self.ddata

    def _single_updated(self, key, dchanges):
        self.changes[2] += 1
        self.log.debug('update | key=%s | dchanges=%s | obj=%s' % (key, dchanges, self.hash_[key]))

    def _single_deleted(self, key):
        self.changes[4] += 1
        self.log.debug('delete | key=%s | obj=%s' % (key, self.hash_[key]))
        obj = self.hash_.pop(key)
        self.list_.remove(obj)

    def _single_create_fail(self, dobj, err=None):
        self.changes[1] += 1
        self.log.error('create failure | dobj=%s | err=%s' % (dobj, format_exc(err)))
        self._excessive_failure_check()

    def _single_update_fail(self, obj, dchanges, err=None):
        self.changes[3] += 1
        self.log.error('update failure | dchanges=%s | obj=%s | err=%s' % (dchanges, obj, format_exc(err)))
        self._excessive_failure_check()

    def _single_delete_fail(self, key, err=None):
        self.changes[5] += 1
        self.log.error('delete failure | key=%s | obj=%s | err=%s' % (key, self.hash_[key], format_exc(err)))
        self._excessive_failure_check()

    def _get_list(self):
        if self._list is None:
            self._list = self._all()
        return self._list
    list_ = property(_get_list)

    def _get_hash(self):
        if self._hash is None:
            self._hash = dict((getattr(o,self.key),o) for o in self.list_ if hasattr(o,self.key))
        return self._hash
    hash_ = property(_get_hash)

    def _clear_cache(self):
        self._list = None
        self._hash = None

    def _excessive_failure_check(self):
        attempts = sum(self.changes)
        fails = sum(self.changes[i] for i in xrange(len(self.changes)) if i%2==0)
        if attempts <= 2: return
        if fails > int(attempts/float(attempts)**0.5+1):
            raise StoreError("Too many failures on this store for this cynq | store=%s | changes=%s"%(self, self.changes))

    def set_arm(self, arm, type_):
        self.arm = arm
        self.type_ = type_
        self.log = logging_helper.get_log('cynq.store.%s.%s'% (self.type_, self.spec.name))




