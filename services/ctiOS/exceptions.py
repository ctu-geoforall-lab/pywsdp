"""
@package ctiOS.exceptions

@brief Base exception classes for ctiOS services

Classes:
 - exceptions::CtiOSError
 - exceptions::CtiOSResponseError
 - exceptions::CtiOSInfo
(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""


class CtiOSError(Exception):
    """General exception for ctiOS errors"""

    def __init__(self, logger, msg):
        logger.fatal(msg)


class CtiOSResponseError(CtiOSError):
    """Basic exception for errors in rows in ctiOS response VFK Gdal db"""

    def __init__(self, logger, msg):
        super().__init__(logger, "{} - {}".format("CTIOS RESPONSE ERROR", msg))


class CtiOSInfo:
    """Info message"""

    def __init__(self, logger, msg):
        logger.info(msg)
