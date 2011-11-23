from stats import Stats

class Base():
    def __init__(self):
        super(Base, self).__init__()
        self._pool = None

    def _pre_cynq(self, cynq_started_at):
        self.stats = Stats(cynq_started_at)
        return True

    def _post_cynq(self):
        return True

    def _pre_cynq_phase(self, phase):
        return True

    def _post_cynq_phase(self, phase):
        return True

    def _create(obj):
        new_obj = self.clone(obj)
        new_obj['_pending_create'] = True
        pool.append(new_obj)
        lenses.

    def _update(source_obj, target_obj=None):
        target_obj = target_obj or 
        
        pool.

    def _all():
        raise NotImplementedError
                
    def _get_pool(self):
        self._pool = self._pool or self._all()




