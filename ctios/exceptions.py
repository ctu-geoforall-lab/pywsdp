"""
@package ctios.exceptions

@brief Exception classes for CTIOS services

Classes:
 - base::CtiOsError
 - base::CtiOsGdalError
 - base::CtiOsResponseError
 - base::CtiOsInfo

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""


class CtiOsError(Exception):
    """General exception for CtiOs errors"""
    def __init__(self, logger, msg):
        logger.fatal(msg)

class CtiOsGdalError(CtiOsError):
    """Basic exception for errors raised by accessing VFK Gdal db"""
    def __init__(self, logger, msg):
        super().__init__(logger, '{} - {}'.format('VFK GDAL DB ERROR', msg))

class CtiOsResponseError(CtiOsError):
    """Basic exception for errors in rows in CtiOs response VFK Gdal db"""
    def __init__(self, logger, msg):
        super().__init__(logger, '{} - {}'.format('CTIOS RESPONSE ERROR', msg))

class CtiOsCsvError(CtiOsError):
    """Basic exception for errors in rows in CtiOs response VFK Gdal db"""
    def __init__(self, logger, msg):
        super().__init__(logger, '{} - {}'.format('CTIOS CSV ERROR', msg))

class CtiOsInfo:
    """Info message for CtiOs info"""
    def __init__(self, logger, msg):
       logger.info(msg)










