"""
@package ctios.csv.exceptions

@brief Exception classes for CTIOS services

Classes:
 - csv::CtiOsCsvError


(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""

from ctios.exceptions import CtiOsError



class CtiOsCsvError(CtiOsError):
    """Basic exception for errors in rows in CtiOs response VFK Gdal db"""
    def __init__(self, logger, msg):
        super().__init__(logger, '{} - {}'.format('CTIOS CSV ERROR', msg))










