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

