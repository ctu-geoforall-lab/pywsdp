"""
@package pywsdp

@brief Base class creating the interface for Sestavy service

Classes:
 - base::SestavyBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""


from base import WSDPBase
from services.sestavy.helpers import SestavyXMLParser


class SestavyBase(WSDPBase):
    """An abstract class that defines interface and main logic
    used for other Sestavy services.
    """
    service_group = "sestavy"

    @property
    def logger(self):
        """A logger object to log messages to"""
        pass

    @property
    def service_name(self):
        """A service name object"""
        pass

    def _parseXML(self, content):
        """Call ctiOS XML parser"""
        return SestavyXMLParser()(
            content=content, logger=self.logger
        )
