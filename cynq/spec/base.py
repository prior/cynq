class Base(object):
    def __init__(self):
        super(Base, self).__init__()
    
    # private methods
    def _default_batch_change(self, change_type, objs):
        if not objs: raise ValueError()
        obj = objs.pop(0)
        success = getattr(self, 'single_%s'%change_type)(obj)
        return (success and [obj] or [], not success and [obj] or [], objs)
    

