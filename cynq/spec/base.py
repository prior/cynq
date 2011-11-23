import copy
from error import StoreError

class BaseSpec(object):
    def __init__(self):
        super(BaseSpec, self).__init__()
    
    # used by default batch implementation so that you can setup a single implementation instead of needing to do batch (though it's very recommended to do batch if you can)
    def _batch_change_using_singles(self, change_type, objs):
        if not objs: raise ValueError()
        objs = list(objs)
        obj = objs.pop(0)
        success = False
        try:
            success = getattr(self, '_single_%s'%change_type)(obj)
        except StoreError:
            pass
        return (success and [obj] or [], not success and [obj] or [], objs)

