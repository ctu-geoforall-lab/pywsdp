"""
@package pywsdp.base

@brief General exception classes for WSDP services

Classes:
 - base::WSDPError
 - base::WSDPRequestError

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""

from base.logger import WSDPLogger


class WSDPError(Exception):
    """Another exception for errors caused by reading, parsing XML"""
    def __init__(self, msg):
        WSDPLogger.fatal(msg)


class WSDPRequestError(WSDPError):
    """Basic exception for errors raised by requesting any WSDP service"""
    def __init__(self, msg):
        super(WSDPRequestError, self).__init__('{} - {}'.format('Service ERROR', msg))


