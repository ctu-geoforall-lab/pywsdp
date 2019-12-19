from ctios.logger import Logger

class CtiOsError(Exception):
    """Another exception for errors caused by reading, parsing XML"""
    def __init__(self, msg):
        Logger.fatal(msg)

class CtiOsDbError(CtiOsError):
    """Basic exception for errors raised by db"""
    def __init__(self, msg):
        super(CtiOsDbError, self).__init__('{} - {}'.format('SQLite3 ERROR', msg))

class CtiOsRequestError(CtiOsError):
    """Basic exception for errors raised by requesting CtiOs service"""
    pass


