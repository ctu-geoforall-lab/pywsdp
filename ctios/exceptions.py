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
    def __init__(self, msg):
        super(CtiOsRequestError, self).__init__('{} - {}'.format('Service ERROR', msg))


class CtiOsResponseError(CtiOsError):
    """Basic exception for errors raised by error in response"""
    def __init__(self, msg):
        super(CtiOsResponseError, self).__init__('{} - {}'.format('XML response ERROR', msg))

