"""
@package ctiOS.csv.exceptions

@brief Exception classes for ctiOS services

Classes:
 - exceptions::CtiOSCsvError


(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""


from services.ctiOS.exceptions import CtiOSError


class CtiOSCsvError(CtiOSError):
    """Basic exception for errors in rows in ctiOS response VFK Gdal db"""

    def __init__(self, logger, msg):
        super().__init__(logger, "{} - {}".format("CTIOS CSV ERROR", msg))
