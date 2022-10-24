"""
@package base.exceptions

@brief General exception classes for WSDP services

Classes:
 - base::WSDPError
 - base::WSDPRequestError
 - base::WSDPResponseError
 
(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""


class WSDPError(Exception):
    """Another exception for errors caused by reading, parsing XML"""

    def __init__(self, logger, msg):
        logger.fatal(msg)


class WSDPRequestError(WSDPError):
    """Basic exception for errors raised by requesting any WSDP service"""

    def __init__(self, logger, msg):
        super().__init__(logger, "{} - {}".format("WSDP REQUEST ERROR", msg))


class WSDPResponseError(WSDPError):
    """Basic exception for errors raised by responses from any WSDP service"""

    def __init__(self, logger, msg):
        super().__init__(logger, "{} - {}".format("WSDP RESPONSE ERROR", msg))
