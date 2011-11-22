class Base(object):
    def __init__(self):
        super(Base, self).__init__()
    
    # private methods
    def _default_batch_change(self, change_type, objs):
        if not objs: raise ValueError()
        obj = objs.pop(0)
        success = False
        try:
            success = getattr(self, 'single_%s'%change_type)(obj)
        except StandardError as err:
            self.log.error(err)
        return (success and [obj] or [], not success and [obj] or [], objs)

    def wrapped_all(self, since=None):
        try:
            self._all(since=since)
        except StandardError as err:
            self.log.error(err)
            raise ListingError(self, err)

    def 

    def wrapped_batch_update(self, change_type, objs):

    def is_too_many_failures(attempt_count, failure_count):
        if attempt_count <= 2: return False
        return failure_count > int(failure_count/float(failure_count)**0.5+1)




