"""
@package ctios.gdal.exceptions

@brief Exception classes for CTIOS services

Classes:
 - gdal::CtiOsGdalError
 - gdal::CtiOsInfo

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""

from ctios.exceptions import CtiOsError



class CtiOsGdalError(CtiOsError):
    """Basic exception for errors raised by accessing VFK Gdal db"""
    def __init__(self, logger, msg):
        super().__init__(logger, '{} - {}'.format('VFK GDAL DB ERROR', msg))

class CtiOsInfo:
    """Info message"""
    def __init__(self, logger, msg):
       logger.info(msg)










