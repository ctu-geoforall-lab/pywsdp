"""
@package ctios.exceptions

@brief Base exception classes for CTIOS services

Classes:
 - exceptions::CtiOsError
 - exceptions::CtiOsResponseError
 - exceptions::CtiOsInfo
(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""


class CtiOsError(Exception):
    """General exception for CtiOs errors"""

    def __init__(self, logger, msg):
        logger.fatal(msg)


class CtiOsResponseError(CtiOsError):
    """Basic exception for errors in rows in CtiOs response VFK Gdal db"""

    def __init__(self, logger, msg):
        super().__init__(logger, "{} - {}".format("CTIOS RESPONSE ERROR", msg))


class CtiOsInfo:
    """Info message"""

    def __init__(self, logger, msg):
        logger.info(msg)
