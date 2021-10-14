"""
@package ctiOS.gdal.exceptions

@brief Exception classes for ctiOS services

Classes:
 - exceptions::CtiOSGdalError

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""


from services.ctiOS.exceptions import CtiOSError


class CtiOSGdalError(CtiOSError):
    """Basic exception for errors raised by accessing VFK Gdal db"""

    def __init__(self, logger, msg):
        super().__init__(logger, "{} - {}".format("VFK GDAL DB ERROR", msg))
