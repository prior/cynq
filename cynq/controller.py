from . import Error
from . import logging_helper
from sanetime import sanetime
from traceback import format_exc

class Controller(object):
    def __init__(self, *arms):
        self.arms = arms
        self.log = logging_helper.get_log('cynq.controller')

    def cynq(self):
        self.errs = []
        self.started_at = sanetime()
        for arm in self.arms: arm.controller = self
        self.cynqable_arms = [arm for arm in self.arms if arm._pre_cynq()]
        if not self.cynqable_arms: return
        self.starting_arms_count = len(self.cynqable_arms)
        try:
            self._cynq_apis()
            self._cynq_local()
            self._cynq_apis()
            self._cynq_local()
            self._cynq_snapshot()
        except StandardError as err:
            self.log.error("giving up on entire cynq | err=%s" % format_exc(err))
        for arm in self.cynqable_arms: arm._post_cynq()
        self.log.info("completed | %s" % ' | '.join(['%s:[api:%s local:%s snapshot:%s]' % (a.spec.name, a.api.changes_tstr, a.local.changes_tstr, a.snapshot.changes_tstr) for a in self.arms]))
        self.log.info("timings | %s | total: %.2f" % (' | '.join(['%s.%s:%s:%.2f' % (a.spec.name, s.type_, t[0], t[1]) for a in self.arms for s in a.stores for t in s.timings if t[1] > 0.1]), (sanetime().ms-self.started_at.ms)/1000.0))
        if self.errs:
            raise Error(self.errs[0])
        return self

    def _cynq_apis(self):
        for arm in list(self.cynqable_arms):
            try:
                if len(self.cynqable_arms)>1: arm.local._clear_cache()
                arm._cynq_api()
            except StandardError as err:
                self.errs.append(err)
                self.log.error("bailing on an arm cynq that threw up an exception during api cynq: err=%s" % format_exc(err))
                self.cynqable_arms.remove(arm)
                if not self.cynqable_arms: raise Error("no more arms left")

    def _cynq_local(self):
        for arm in list(self.cynqable_arms):
            try:
                if len(self.cynqable_arms)>1: arm.local._clear_cache()
                arm._cynq_local()
            except StandardError as err:
                self.errs.append(err)
                self.log.error("bailing on an arm cynq that threw up an exception during snapshot cynq: err=%s" % format_exc(err))
                self.cynqable_arms.remove(arm)
                if not self.cynqable_arms: raise Error("no more arms left")

    def _cynq_snapshot(self):
        for arm in list(self.cynqable_arms):
            try:
                if len(self.cynqable_arms)>1: arm.local._clear_cache()
                arm._cynq_snapshot()
            except StandardError as err:
                self.errs.append(err)
                self.log.error("bailing on an arm cynq that threw up an exception during snapshot cynq: err=%s" % format_exc(err))
                self.cynqable_arms.remove(arm)
                if not self.cynqable_arms: raise Error("no more arms left")

    def _get_complete_success(self):
        return len(self.cynqable_arms) == self.starting_arms_count and self.started_at
    complete_success = property(_get_complete_success)


