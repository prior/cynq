from .. import Error,StoreError
from .. import logging_helper
from copy import deepcopy
from traceback import format_exc
from sanetime import sanetime


class BaseStore(object):
    TRANSLATION = {} # or a hash that has spec attr as a key and this store's specific attr as the value

    # all the methods available to override (but should not be called directly by you ever!)
    def _all(self): raise NotImplementedError(str(self.__class__))
    
    # you can choose to implement just the bulk ones or just the single ones-- not really a need to implement both
    def _bulk_create(self, create_tuples): raise NotImplementedError() # return obj,dobj,keyless_trigger tuples (obj is None on failure) (create_tuple=(dobj,keyless_trigger))    exceptions unnecessary(will get picked up in unsuccesses) 
    def _bulk_update(self, update_tuples): raise NotImplementedError()  # return success,obj,djchanges tuples (update_tuple=(obj, dchanges))    throwing exceptions unnecessary(will get picked up in unsuccesses) 
    def _bulk_delete(self, objs): raise NotImplementedError() # return success,obj tuples    exceptions unnecessary(will get picked up in unsuccesses) 

    def _single_create(self, dobj): raise NotImplementedError()  # returns new obj   throws exception on error
    def _single_update(self, obj, dchanges): raise NotImplementedError()  # returns obj with changes  throws excption on error   
    def _single_delete(self, obj): raise NotImplementedError()  # returns obj if   throws exception on error

    def _pre_cynq(self): return True
    def _post_cynq(self): return True

    def _createable(self, arm): return True
    def _updateable(self, arm): return True
    def _deleteable(self, arm): return True


    # public methods
    def bulk_create(self, tuples):
        if not tuples: return
        start_time = sanetime()
        if not self._createable(self.arm): return # avoid error reporting since this is on purpose
        try:
            for obj,dobj,keyless_trigger in self._bulk_create(tuples):
                if obj: self._single_created(obj, dobj, keyless_trigger)
                else: self._single_create_fail(dobj, keyless_trigger)
        except NotImplementedError:
            for dobj,keyless_trigger in tuples:
                self.single_create(dobj, keyless_trigger)
        self.timings.append(("creates", (sanetime().ms - start_time.ms)/1000.0))

    def single_create(self, dobj, keyless_trigger=None):
        try:
            obj = self._single_create(dobj)
            self._single_created(obj, dobj, keyless_trigger)
        except NotImplementedError:
            raise Error("You need to implement either the _single_create or the _bulk_create [%s: %s: %s]" % (self.__class__.__name__, self.spec.name, self.type_))
        except StandardError as err:
            self._single_create_fail(dobj, keyless_trigger, err)


    def bulk_update(self, tuples):
        if not tuples: return
        start_time = sanetime()
        if not self._updateable(self.arm): return  # avoid error reporting since this is on purpose
        try:
            for success,obj,dchanges in self._bulk_update(tuples):
                if success: self._single_updated(obj, dchanges)
                else: self._single_update_fail(obj, dchanges)
        except NotImplementedError:
            for obj,dchanges in tuples:
                self.single_update(obj, dchanges)
        self.timings.append(("updates", (sanetime().ms - start_time.ms)/1000.0))

    def single_update(self, obj, dchanges):
        try:
            self._single_update(obj, dchanges)
            self._single_updated(obj, dchanges)
        except NotImplementedError:
            raise Error("You need to implement either the _single_update or the _bulk_update")
        except StandardError as err:
            self._single_update_fail(obj, dchanges, err)

    def bulk_delete(self, objs):
        if not objs: return
        start_time = sanetime()
        if not self._deleteable(self.arm): return # avoid error reporting since this is on purpose
        try:
            for success,obj in self._bulk_delete(objs):
                if success: self._single_deleted(obj)
                else: self._single_delete_fail(obj)
        except NotImplementedError:
            for obj in objs:
                self.single_delete(obj)
        self.timings.append(("deletes", (sanetime().ms - start_time.ms)/1000.0))

    def single_delete(self, obj):
        try:
            self._single_delete(obj)
            self._single_deleted(obj)
        except NotImplementedError:
            raise Error("You need to implement either the _single_delete or the _bulk_delete")
        except StandardError as err:
            self._single_delete_fail(obj, err)

    def apply_changeset(self, changeset):
        self.bulk_create([(self._bulk_translate(v),None) for v in changeset.creates.values()])
        self.bulk_update([(self.hash_[self._translate(t[0])],self._bulk_translate(t[1])) for t in changeset.updates.iteritems()])
        self.bulk_delete([self.hash_[self._translate(key)] for key in changeset.deletes])
        self.bulk_create([(self._bulk_translate(v[0]),v[1]) for v in changeset.keyless_creates.values()])

    def generate_update_trigger(self, obj):
        def trigger(new_key_value):
            self.bulk_update([(obj, {self._translate(self.key) : new_key_value})])
        return trigger


    #private methods
    def __init__(self):
        super(BaseStore, self).__init__()
        self.arm, self.type_, self.spec = None,None,None # will get set by owning arm during cynq setup
        self._clear_cache()
        self.changes = [0,0,0,0,0,0] #success/fails for create/update/delete
        self.timings = []
        self.translation = deepcopy(self.__class__.TRANSLATION)

    def with_arm(self, arm, type_):
        self.arm = arm
        self.type_ = type_
        self.spec = arm.spec
        self.key = self.spec.key
        self.log = logging_helper.get_log('cynq.store.%s.%s'% (self.type_, self.spec.name))
        return self

    def _single_created(self, obj, dobj, keyless_trigger=None):
        self.changes[0] += 1
        self.log.debug('create | key=%s | dobj=%s | obj=%s | keyless_trigger=%s' % (getattr(obj,self._translate(self.key)), dobj, obj, keyless_trigger))
        self.list_.append(obj)
        self.hash_[getattr(obj,self._translate(self.key))] = obj
        if keyless_trigger: keyless_trigger(getattr(obj, self._translate(self.key)))

    def _single_updated(self, obj, dchanges):
        self.changes[2] += 1
        self.hash_[getattr(obj, self._translate(self.key))] = obj
        self.log.debug('update | key=%s | dchanges=%s | obj=%s' % (getattr(obj, self._translate(self.key)), self._bulk_translate(dchanges), obj))

    def _single_deleted(self, obj):
        self.changes[4] += 1
        self.log.debug('delete | key=%s | obj=%s' % (getattr(obj, self._translate(self.key)), obj))
        obj = self.hash_.pop(getattr(obj, self._translate(self.key)))
        self.list_.remove(obj)

    def _single_create_fail(self, dobj, keyless_trigger=None, err=None):
        self.changes[1] += 1
        self.log.error('create failure | dobj=%s | keyless_trigger=%s | err=%s' % (dobj, keyless_trigger, format_exc(err)))
        self._excessive_failure_check()

    def _single_update_fail(self, obj, dchanges, err=None):
        self.changes[3] += 1
        self.log.error('update failure | dchanges=%s | key=%s | obj=%s | err=%s' % (self._bulk_translate(dchanges), getattr(obj, self._translate(self.key)), obj, format_exc(err)))
        self._excessive_failure_check()

    def _single_delete_fail(self, obj, err=None):
        self.changes[5] += 1
        self.log.error('delete failure | key=%s | obj=%s | err=%s' % (getattr(obj, self._translate(self.key)), obj, format_exc(err)))
        self._excessive_failure_check()

    def _sanity_check_list(self): # to prevent any doubles
        key_values = set()
        for o in self.list_:
            key_value = getattr(o, self._translate(self.key), None)
            if key_value in key_values:
                raise StoreError("list is not unique on key=%s, key_value=%s [obj: %s]" % (self.key, key_value, o.__dict__))
            if key_value: key_values.add(key_value)

    def _get_list(self):
        if self._list is None:
            start_time = sanetime()
            self._list = list(self._all())
            self.timings.append(("reads", (sanetime().ms - start_time.ms)/1000.0))
        return self._list
    list_ = property(_get_list)

    def __len__(self):
        return len(self.list_)

    def _get_hash(self):
        if self._hash is None:
            self._sanity_check_list()
            self._hash = dict((getattr(o,self._translate(self.key)),o) for o in self.list_ if getattr(o,self._translate(self.key),None) is not None)
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



    def _translate(self, dattr): 
        return self.translation.get(dattr,dattr)

    def _backward_translate(self, dattr):
        if not hasattr(self, 'backward_translation'):
            self.backward_translation = dict((v,k) for k,v in self.translation.iteritems())
        return self.backward_translation.get(dattr,dattr)

    def _bulk_translate(self, dhash):
        return dict((self._translate(k),v) for k,v in dhash.iteritems())

    def _bulk_backward_translate(self, dhash):
        return dict((self._backward_translate(k),v) for k,v in dhash.iteritems())

        
    def dscoped(self, obj, spec_attrs, setup_keyless_trigger=False):
        keyless_trigger = None
        d = dict((a,getattr(obj,self._translate(a),None)) for a in spec_attrs) 
        if setup_keyless_trigger:
            keyless_trigger = self.generate_update_trigger(obj)
        return setup_keyless_trigger and (d, keyless_trigger) or d

    def ddiff(self, key_value, spec_attrs, to_store):
        from_obj = self.hash_[key_value]
        to_obj = to_store.hash_[key_value]
        return dict((a,getattr(from_obj,self._translate(a),None)) for a in spec_attrs if getattr(from_obj,self._translate(a),None) != getattr(to_obj,to_store._translate(a),None))


    def _get_changes_tstr(self):
        return "(%s,%s,%s,%s,%s,%s)" % tuple(self.changes)
    changes_tstr = property(_get_changes_tstr)
