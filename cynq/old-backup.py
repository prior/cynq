
STORE_DESIGNATIONS = [
    'key_attribute',
    'common_attributes',
    'owned_attributes',
    'remote_existence_attribute' ]


class CacheStore(BaseStore):
    def __init__(self, store):
        super(StoreCache,self).__init__()
        self.store = store

    def list_(self):
        if getattr(self,'list_cache', None) == None:
            self.list_cache = self.store.list_()
        return self.list_cache

    def update(self, obj):
        return self.store.update(obj)

    def create(self, obj):
        return self.store.create(obj)

    def delete(self, obj):
        return self.store.delete(obj)

    #TODO: figure out how to sync a single object instead of a list -- this method is just conjecture for now
    def get(self, id_):
        if getattr(self, 'list_cache', None) == None:
            self.list_cache = [self.store.get(id_)]

    def __iter__(self):
        return iter(self.list_())


    def 

class FacetedCacheStore(BaseStore):
    def __init__(self, store, key_name=None):
        super(StoreFacetCache,self).__init__()
        self.store = store
        key_name = key_name or self.store.key_name
        self.hash_cache = dict((getattr(o,key_name),o) for o in self.store if getattr(o,key_name,None))

    def __getitem__(self, key):
        self.hash_cache[key]

    def list_(self):
        self.hash_cache

    def update(self, obj):
        return self.store.update(obj)

    def create(self, obj):
        return self.store.create(obj)

    def delete(self, obj):
        return self.store.delete(obj)

class FacetedStoreCache(object):
    def __init__(self, store, key_names=None):
        super(StoreCache,self).__init__()
        self.store = store
        self.key_names = key_names or [self.store.key_name]
        self.list_cache = self.store.list_()
        for key_name in key_names:
            self.hash_cache[key_name] = dict((getattr(o,key_name),o) for o in self.list_cache if getattr(o,key_name,None))

    def 
    def _list


class SyncFacet(BaseStore):
    def __init__(self, store, key_name=None):
        super(SyncFacet,self).__init__()
        self.store = store
        self.key_name = key_name or self.store.key_name
        self.hash_cache = dict((getattr(o,self.key_name),o) for o in self.list_cache)
        
    def __getitem__(self, key):
        self.hash_cache[key]

class Model(object):
    deleted_at = DateTimeField()
    has_remote
    hubspot_syncable_udpated_at
    webinar_syncable_updated_at


delted_at AND has_remote == pending outbound_delete
deleet_at AND not has_remote == nothing
no deleted and has_remote = nothing
no deleted and not has_remote == pending outbound create
no deleted and has_remote and (hubspot/webinar)updated_at > synced_at == pending outbound update
remote_synced_at (hubspot_synced_at, webinar_synced_at)

exists_in_remote(hubspot/webinar) -- boolean


class CachedStore
    def __init__(self, store):
        this.store = store
        self.list_cache = self.store.list_()
        self.creates

    def create(self, obj)
        creates = set[obj]
        self.list_cache.append(obj)

    def udpate(self, obj)
        updates = [obj]
        
    def flush(self):
        for obj in self.creates:
            this.store.create(obj)


class WriteCachedStore(ProxyStore):
    def __init__(self, store):
        super(WriteCachedStore,self).__init__(store)
        self.creates = []
        self.updates = []
        self.deleted = []

    def create(self, obj):
        self.creates.append(obj)
        return obj

    def update(self, obj):
        self.updates.append(obj)
        return obj

    def delete(self, obj):
        self.deletes.append(obj)
        return obj
        
    def flush(self):
        done = []
        for create_obj in self.creates:
            self.store.create(create_obj)
        for update_obj in self.updates:
            if update_obj not in create_obj:
                self.store.update(update_obj)
        for delete_obj in self.delete:
            self.store.delete(delete_obj)

# lazy list cache
class FacetedReadCachedStore(ProxyStore):
    def __init__(self, store):
        super(FacetedCachedStore,self).__init__(store)

    def get_facet(self, key_name)
        facet = facets.get(key_name,None)
        if not facet:
            facet = facets[key_name] = Facet(self, key_name)
        return facet

    def create(self, *args, **kwargs)
        obj = self.store.create(*args, **kwargs)  
        if obj:
            self.list_().append(obj)
            for facet in facets:
                facet.key_created_if_not_exists(obj)
        return obj

    def update(self, *args, **kwargs)
        obj = self.store.update(*args, **kwargs)  
        if obj:
            for facet in facets:
                facet.key_created_if_not_exists(obj)
        return obj

    def delete(self, *args, **kwargs)
        obj = self.store.delete(*args, **kwargs)
        if obj:
            self.list_().delete(obj)
            for facet in facets:
                facet.key_deleted_if_exists(obj)
        return obj

    def list_(self):
        if not getattr(self, 'list_cache', None):
            self.list_cache = self.store.list_()
        return self.list_cache


# lazy hash cache
class Facet(ProxyStore):
    def init(self, store, key_name)
        super(Facet,self).__init__(store)
        self.key_name = key_name

    def list_(self)
        return self.dict_().values()

    def dict_(self):
        if not getattr(self, 'dict_cache', None):
            self.dict_cache = self.store.list_()
        return self.dict_cache
        
    def __iter__(self):
        return iter(self.dict_())

    def __contains__(self, key):
        return key in self.dict_()

    def __getitem__(self, key):
        return self.dict_().get(key, None)

    def __and__(self, other): # other must also be a Facet
        return set(self) & set(other)

    def __sub__(self, other): # other must also be a Facet
        return set(self) - set(other)

    def key_created_if_not_exists(self, obj):
        key_value = getattr(obj, self.key_name)
        self.dict_()[key_value] = obj

    def key_deleted_if_exists(self, obj):
        key_value = getattr(obj, self.key_name)
        if key_value in self.dict_():
            del self.dict_()[key_value]





class LocalFacet(Facet):
    def __init__(self, store, key_name, remote_expectation_attr_name):
        super(LocalFacet,self).__init__(store, key_name)
        self.remote_expectation_attr_name = remote_expectation_attr_name

    def create(self, obj):
        setattr(obj, self.remote_expectation_attr_name, True)
        super(LocalFacet,self).create(obj)

    def update(self, obj):
        setattr(obj, self.remote_expectation_attr_name, True)
        super(LocalFacet,self).update(obj)
        
    def delete(self, obj):
        super(LocalFacet,self).delete(obj)
        setattr(obj, self.remote_expectation_attr_name, True)

    # must ensure remote existence is set if local
    create():

    # must ensure remote existence is set if local
    update():

    # must ensure remote existence is set if local
    delete():

# model must have 'deleted_at', and 'exists_in_webinar' and 'exists_in_hubspot', and 'syncable_updated_at'
class SyncConnection(object):
    def __init__(self, local_facet, remote_facet):
        super(SyncConnection,self).__init__()
        self.local = local_facet
        self.remote = remote_facet

    def inbound_create(self):
        for key in self.remote():
            if key not in self.local:
                self.log.debug('Creating new object in local cache...')
                self.local.create(self.remote[key])
            else:  #looking for reanimate possibility
                local_obj = self.local[key]
                if self.local_obj.deleted_at and not self._has_remote_expectation(local_obj):
                    self.log.debug('Reanimating object in local cache...')
                    self.local.create(self.remote[key])
                    self.ensure_remote_expectation(local_obj)

    def inbound_update(self):
        for local_key in (self.local & self.remote):
            local_obj = self.local[local_key]
            if not local_obj.deleted_at and not self._has_local_changed_since_last_sync(local_obj):
                remote_obj = self.remote[local_key]
                self.log.debug('Updating object in local cache...')
                self.local.update(self.merge_object(local_obj,remote_obj))
                self.ensure_remote_expectation(local_obj)

    def inbound_delete(self):
        for local_key in (self.local - self.remote):
            local_obj = self.local[local_key]
            if not local_obj.deleted_at and self._has_remote_expectation(local_obj):
                self.log.debug('Deleting local object...')
                self.local.delete(local_obj)
                self.remove_remote_expectation(local_obj)

    def outbound_delete(self):
        for local_key in (self.local & self.remote):
            local_obj = self.local[local_key]
            if local_obj.deleted_at and self._has_remote_expectation(local_obj):
                self.log.debug('Deleting remote object...', local_obj=local_obj)
                self.remote.delete(local_obj)
                self.remove_remote_expectation(local_obj)

    def outbound_update(self):
        for local_obj in (self.local & self.remote):
            if not local_obj.deleted_at:
                self.log.debug('Updating remote object...')
                self.remote.update(local_obj)

    def outbound_create(self):
        for local_obj in (self.local - self.remote):
            if not local_obj.deleted_at and not self._has_remote_expectation(local_obj):
                self.log.debug('Creating remote object...')
                self.local.update(self.remote.create(local_obj))



    def _has_remote_expectation(self, local_obj):
        return getattr(local_obj, self.remote.remote_expectation_attribute)

    def _set_expected_in_remote(self, obj, value=False):
        setattr(obj, self.remote.expected_in_remote_attr_name, True)

    def _has_local_changed_since_last_sync(self, local_obj):
        synced_at = local_obj.synced_at
        syncable_updated_at = local_obj.syncable_updated_at
        return synced_at and syncable_updated_at and syncable_updated_at > synced_at

    def merged_object(self, target, source):
        for attr in self.remote.syncable_attributes + [self.remote.remote_expectation_attribute]:
            setattr(target, attr, getattr(source, attr, None))
        return target




class LocalStore(BaseStore):
    communal_attributes = []
    owned_attributes = []
    key_attribute = None

class ProxyStore(BaseStore):
    def __init__(self, store):
        super(ProxyStore, self).__init__()
        self.store = store
        for attr in STORE_DESIGNATIONS:
            if getattr(store, attr, None):
                self.key_attribute = store.key_attribute

    def list_(self):
        return self.store.list_()

    def create(self, obj):
        return self.store.create(obj)

    def update(self, obj):
        return self.store.update(obj)

    def delete(self, obj):
        return self.store.delete(obj)
    

class RemoteGlove(ProxyStore):
    def __init__(self, remote_store):
        super(RemoteGlove,self).__init__(store)
        self.creates = []
        self.updates = []
        self.deleted = []

    def create(self, obj):
        self.creates.append(obj)
        return obj

    def update(self, obj):
        self.updates.append(obj)
        return obj

    def delete(self, obj):
        self.deletes.append(obj)
        return obj
        
    def flush(self):
        done = []
        for create_obj in self.creates:
            self.store.create(create_obj)
        for update_obj in self.updates:
            if update_obj not in create_obj:
                self.store.update(update_obj)
        for delete_obj in self.delete:
            self.store.delete(delete_obj)



class RemoteStoreGlove(ProxyStore):
    communal_attributes = []
    owned_attributes = []
    key_attribute = None
    remote_expectation_attribute = None

    def __init__(self, store):
        super(RemoteStore, self).__init__(store)
        self.store = store
        self.remote_expectation_attribute = self.__class__.remote_expectation_attribute

    def list_(self):
        l = self.store.list_()
        for o in l:
            setattr(o, self.store.remote_expectation_attribute, True)
        return l

    def create(self, obj):
        obj = self.store.create(obj)
        if obj:
            setattr(o, self.remote_expectation_attribute, True)
        return obj

    def update(self, obj):
        obj = self.store.update(obj)
        if obj:
            setattr(o, self.remote_expectation_attribute, True)
        return obj
        ob





class Controller(object):
    def __init__(self, local_store, remote_stores):
        super(Controller,self).__init__()
        self.write_cached_local = WriteCachedStore(local_store)
        self.local = FacetedReadCachedStore(self.write_cached_local)
        self.connections = []
        for remote in remotes:
            remote_faceted_store = FacetedReadCachedStore(RemoteGlove(remote))
            key_attribute = remote.key_attribute
            remote_facet = remote_faceted_store.get_facet(key_attribute)
            local_facet = self.local_faceted_store.get_facet(key_attribute)
            conn = Connection(local_facet, remote_facet)
            self.connection.append(conn)

    def sync():
        self._inbound_create()
        self._inbound_update()
        self._inbound_delete()
        self._outbound_delete()
        self._outbound_update()
        self._outbound_create()
        self.write_cached_local.flush()

    def _inbound_create():
        for conn in self.connections:
            self.inbound_create()

    def _inbound_update():
        for conn in self.connections:
            self.inbound_update()

    def _inbound_delete():
        for conn in self.connections:
            self.inbound_delete()

    def _outbound_delete():
        for conn in self.connections:
            self.outbound_delete()

    def _outbound_update():
        for conn in self.connections:
            self.outbound_update()

    def _outbound_create():
        for conn in self.connections:
            self.outbound_create()





