"""
@package pywsdp.base

@brief Exception classes for CTIOS services

Classes:
 - base::CtiOsError
 - base::CtiOsInfo

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""


from pywsdp.base.logger import WSDPLogger



class CtiOsError(Exception):
    """General exception for CtiOs errors"""
    def __init__(self, msg):
        WSDPLogger.fatal(msg)

class CtiOsInfo:
    """Info message for CtiOs info"""
    def __init__(self, msg):
        WSDPLogger.info(msg)







