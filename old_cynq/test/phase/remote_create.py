

class RemoteSpec(Spec):




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

