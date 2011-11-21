class Error(Exception):
    """Base class for exceptions in this package"""
    pass

class ConnectionPhaseError(Error):
    """Exception raised when a connection phase fails either partially or fully

    Attributes:
        expr

    """
    pass

class ChangeError(Error):
    """Exception when trying to persist a change"""
    pass


