class CtiOsDbError(Exception):
    """Basic exception for errors raised by db"""
    pass


class CtiOsRequestError(Exception):
    """Basic exception for errors raised by requesting CtiOs service"""
    pass


class CtiOsError(Exception):
    """Another exception for errors caused by reading, parsing XML"""
    pass
