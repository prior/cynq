from sanetime import sanetime
from cynq.error import Error
from cynq import logging_helper
from traceback import format_exc

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
            if len(self.cynqable_arms)>=2: self._cynq_apis()  # only needed if we still got 2 or more hooked up
            self._cynq_snapshot()
        except StandardError as err:
            self.log.error("giving up on entire cynq | err=%s" % format_exc(err))
        for arm in self.cynqable_arms: arm._post_cynq()
        return self

    def _cynq_apis(self):
        for arm in list(self.cynqable_arms):
            try:
                arm._cynq_api()
            except StandardError as err:
                self.log.error("bailing on an arm cynq that threw up an exception during api cynq: err=%s" % format_exc(err))
                self.cynqable_arms.remove(arm)
                if not self.cynqable_arms: raise Error("no more arms left")

    def _cynq_local(self):
        for arm in list(self.cynqable_arms):
            try:
                arm._cynq_local()
            except StandardError as err:
                self.log.error("bailing on an arm cynq that threw up an exception during snapshot cynq: err=%s" % format_exc(err))
                self.cynqable_arms.remove(arm)
                if not self.cynqable_arms: raise Error("no more arms left")

    def _cynq_snapshot(self):
        for arm in list(self.cynqable_arms):
            try:
                arm._cynq_snapshot()
            except StandardError as err:
                self.log.error("bailing on an arm cynq that threw up an exception during snapshot cynq: err=%s" % format_exc(err))
                self.cynqable_arms.remove(arm)
                if not self.cynqable_arms: raise Error("no more arms left")


