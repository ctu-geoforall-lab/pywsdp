from ctios.logger import Logger


class WSDPError(Exception):
    """Another exception for errors caused by reading, parsing XML"""
    def __init__(self, msg):
        Logger.fatal(msg)


class WSDPRequestError(WSDPError):
    """Basic exception for errors raised by requesting CtiOs service"""
    def __init__(self, msg):
        super(WSDPRequestError, self).__init__('{} - {}'.format('Service ERROR', msg))


