"""
@package ctios.core

@brief Base abstract class creating the interface for CTIOS services

Classes:
 - ctios::CtiOs

(C) 2021 Linda Kladivova l.kladivova@seznam.cz
This library is free under the GNU General Public License.
"""

import os

from ctios.helpers import CtiOsXMLParser, CtiOsCounter
from base import WSDPBase
from base.template import WSDPTemplate
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

    def renderXML(self, ids_array):
        """Render xml request from ids array."""
        request_xml = WSDPTemplate(self.template_path).render(username=self._username, password=self._password,
            posidents=''.join(ids_array)
        )
        return request_xml

    def parseXML(self, content, counter):
        """Call CtiOs XML parser"""
        return CtiOsXMLParser()(content=content,
                           counter=counter,
                           logger=self.logger)

    def getXMLresponse(self, ids_array):
        """Call service, render XML response and parse it to dictionary"""
        counter = CtiOsCounter()
        xml = self.renderXML(ids_array)
        response_xml = self.call_service(xml)
        dictionary = self.parseXML(response_xml, counter)
        print(dictionary)
        return dictionary

