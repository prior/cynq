from . import Error
from . import logging_helper
from sanetime import sanetime
from traceback import format_exc

#TODO: add extra caching level for local so we don't have to get all rows constantly (we'd need a surface cache focused ona specific spec, but underneath the raw list... should be pretty easy)

class Controller(object):
    def __init__(self, *arms):
        self.arms = arms
        self.log = logging_helper.get_log('cynq.controller')

    def cynq(self):
        self.started_at = sanetime()
        for arm in self.arms: arm.controller = self
        self.cynqable_arms = [arm for arm in self.arms if arm._pre_cynq()]
        if not self.cynqable_arms: return
        try:
            self._cynq_apis()
            self._cynq_local()
            if len(self.cynqable_arms)>1: self._cynq_apis()  # only needed if we still got 2 or more hooked up
            self._cynq_snapshot()
        except StandardError as err:
            self.log.error("giving up on entire cynq | err=%s" % format_exc(err))
        for arm in self.cynqable_arms: arm._post_cynq()
        return self

    def _cynq_apis(self):
        for arm in list(self.cynqable_arms):
            try:
                if len(self.cynqable_arms)>1: arm.local._clear_cache()
                arm._cynq_api()
            except StandardError as err:
                self.log.error("bailing on an arm cynq that threw up an exception during api cynq: err=%s" % format_exc(err))
                self.cynqable_arms.remove(arm)
                if not self.cynqable_arms: raise Error("no more arms left")

    def _cynq_local(self):
        for arm in list(self.cynqable_arms):
            try:
                if len(self.cynqable_arms)>1: arm.local._clear_cache()
                arm._cynq_local()
            except StandardError as err:
                self.log.error("bailing on an arm cynq that threw up an exception during snapshot cynq: err=%s" % format_exc(err))
                self.cynqable_arms.remove(arm)
                if not self.cynqable_arms: raise Error("no more arms left")

    def _cynq_snapshot(self):
        for arm in list(self.cynqable_arms):
            try:
                if len(self.cynqable_arms)>1: arm.local._clear_cache()
                arm._cynq_snapshot()
            except StandardError as err:
                self.log.error("bailing on an arm cynq that threw up an exception during snapshot cynq: err=%s" % format_exc(err))
                self.cynqable_arms.remove(arm)
                if not self.cynqable_arms: raise Error("no more arms left")


