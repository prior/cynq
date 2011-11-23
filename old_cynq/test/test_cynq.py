import unittest2
from cynq.test import helper
from sanetime import sanetime

import logger
logger.configure_log()


class GoodStore(Base): pass
class BadStore(Base):
    def pre_cynq(): return False


class CynqTest(unittest2.TestCase):
    def setUp(self):
        remote_store = 
        self.remote_store = TestRemote()
        self.remote = Facet(self.remote_store, 'key')
        self.local_store = TestLocal()
        self.local = Facet(self.local_store, 'key')
        self.conn = Connection(self.local, self.remote)

    def tearDown(self):
        pass

    def test_bad_local_cynq(self):


        self.assertNoAction(Cynq(BadStore(), (GoodStore(), GoodStore())))
        self.assertNoAction(Cynq(GoodStore(), (BadStore(), BadStore())))
        self.assertAction(Cynq(GoodStore(), (BadStore(), GoodStore())))


    def assert_no_action(self, cynq):
        test_phase = TestPhase()
        cynq.connection_phases = [TestPhase]
        cynq.cynq()

        assertFalse(test_phase.was_executed)

