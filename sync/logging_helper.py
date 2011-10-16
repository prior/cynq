import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

def get_package_logger(subname=''):
    subname = subname.strip()
    if subname:
        subname = '.%s'%subname
    h = NullHandler()
    logger = logging.getLogger('sync%s'%subname)
    logger.addHandler(h)
    return logger

