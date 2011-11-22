from base import Base
from cynq import Cynq

class LocalBase(Base):
    def __init__(self):
        super(LocalBase, self).__init__()

    def cynq(self, remote_stores):
        return Cynq(self, remote_stores).cynq()



