"""
@package ctios.core

@brief Base abstract class creating the interface for CTIOS services

Classes:
 - ctios::CtiOs

(C) 2021 Linda Kladivova l.kladivova@seznam.cz
This library is free under the GNU General Public License.
"""

import os

from ctios.helpers import CtiOsXMLParser
from base import WSDPBase
from base.logger import WSDPLogger


logger = ctios_logger = WSDPLogger("pyctios")


class CtiOs(WSDPBase):
    """A concrete creator that creates a CtiOs class and sets in runtime all its attributes."""

    logger = ctios_logger

    def get_service_name(self):
        """Method for getting service name"""
        return "ctios"

    def get_default_log_dir(self):
        """Method for getting default log dir"""
        return os.path.join(os.path.abspath('logs'), 'ctios')

    def get_default_out_dir(self):
        """Method for getting default output dir"""
        return os.path.join(os.path.abspath('tests'), 'output_data')

    def parseXML(self, content, counter):
        """Call CtiOs XML parser"""
        return CtiOsXMLParser()(content=content,
                           counter=self.counter,
                           logger=self.logger)

