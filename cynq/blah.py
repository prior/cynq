

class RemoteStore1(object):
    # all options possible
    pushed = ['one']
    pulled = ['two']
    shared = ['key','share']
    key = 'key'

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


def test_createable():
    class RS(RemoteTestStore): createable=False
    rs = RS([])
    l = LocalStore(


    r1 = RemoteStore1







def test
    


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
