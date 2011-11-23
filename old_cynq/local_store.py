import logging_helper

class BaseLocalStore(BaseStore):
    def __init__(self):
        super(BaseLocalStore, self).__init__()

    def cynq(self, remote_stores):
        return Cynq(self, remote_stores).cynq()

