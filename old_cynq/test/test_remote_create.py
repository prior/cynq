class RemoteMemorySpec(Spec):
    def __init__(self, seeds=None):
        super(MemorySpec, self).__init__()
        self.hash_ = self.hashify_list(seeds or [])

    def all_():
        return self.hash_.values()

    def create(obj):
        for attr in self.pushed:
            obj[attr] = str(uuid.uuid4())
        self.hash_[obj[self.key]] = obj
        return obj

    def update(obj):
        for attr in self.pushed:
            if obj.get(attr) is None:
                obj[attr] = str(uuid.uuid4())
        self.hash_[obj[self.key]] = obj
        return obj

    def delete(obj):
        del self.hash_[obj[self.key]]



class RemoteSpec(Spec):
    def hashify_list(self, list_):
        dict((o.get(self.key), o) for o in list_)
        




class RemoteStore1(object):
    # all options possible
    pushed = ['one']
    pulled = ['two']
    shared = ['key','share']
    key = 'key'
    since = 'updated_at'

    createable = True
    deleteable = True
    updateable = True
    sinceable = True

    def all_():
        pass

    def delete():
        pass

    def update():
        pass

    def create():
        pass

    
class RemoteStore2(object):
    pushed = ['two']
    pulled = ['one']
    shared = ['key','share']
    key = 'key'

class Local(object):
    createable = True
    updateable = True
    deleteable = ('soft','deleted_at')
    sinceable = True


def test_remote_create():
    r = TestRemoteSpec([{'key':True, 'one':1, 'two':1, 'shared':1}])
    l = TestLocalSpec()
    j = Junction(l,r)
    p = RemoteCreateJunctionPhase(j)
    p.execute()




    r2 = RemoteStore2([{'key':True, 'two':2, 'one':2, 'shared':2}])
    r1 = RemoteSpec1(


def test_createable():
    rs = RemoteTestStore([])
    l = LocalStore(self.local_seed)
    l.out_create(rs)
    self.assertEquals(self.local_seed, l.all_())

    class RS(RemoteTestStore): createable=False
    rs = RS([])
    l = LocalStore(self.local_seed)
    l.out_create(rs)
    self.assertEquals(self.local_seed, l.all_())
    rs.all_()



def test_ordering_of_inbound_changes():
    r1 = RemoteStore1([{'key':True, 'one':1, 'two':1, 'shared':1}])
    r2 = RemoteStore2([{'key':True, 'two':2, 'one':2, 'shared':2}])
    l = LocalStore()
    l.cynq(r1,r2)
    self.assertEquals(1, len(l))
    self.assertTrue(l[0]['key'])
    self.assertEquals(1, l[0]['one'])
    self.assertEquals(2, l[0]['two'])
    self.assertEquals(2, l[0]['shared'])

def test_ordering_of_inbound_changes():
    r1 = RemoteStore1([{'key':True, 'one':1, 'two':1, 'shared':1}])
    r2 = RemoteStore2([{'key':True, 'two':2, 'one':2, 'shared':2}])
    l = LocalStore()
    l.cynq(r1,r2)
    self.assertEquals(1, len(l))
    self.assertTrue(l[0]['key'])
    self.assertEquals(1, l[0]['one'])
    self.assertEquals(2, l[0]['two'])
    self.assertEquals(2, l[0]['shared'])

    normal_remote1, normal_remote2)
    local['

    
local.cynq(remote1, remote2)
