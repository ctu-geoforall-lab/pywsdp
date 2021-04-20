"""
@package ctios
@brief Base abstract class creating the interface for CTIOS services

Classes:
 - ctios::CtiOs

(C) 2021 Linda Kladivova l.kladivova@seznam.cz
This library is free under the GNU General Public License.
"""


from base.helpers import CtiOsXMLParser, CtiOsCounter
from pywsdp.base.core import WSDPBase
from pywsdp.base.helpers import WSDPTemplate



class CtiOs(WSDPBase):
    """A concrete creator that creates a CtiOs class and sets in runtime all its attributes."""

    def get_service_name(self):
        """Method for getting service name"""
        return "ctios"

    def define_log_name(self):
        """Method for defining logger name according to service"""
        return "pyctios"

    def renderXML(self, ids_array):
        """Render xml request from ids array."""
        request_xml = WSDPTemplate(self.template_dir).render(
            self._config['files']['request_xml_file'], username=self._username, password=self._password,
            posidents=''.join(ids_array)
        )
        return request_xml

    def parseXML(self, content, counter, logger):
        """Call CtiOs XML parser"""
        return CtiOsXMLParser(content=content,
                           counter=counter,
                           logger=logger)

    def getXMLresponse(self, ids_array):
        """Call service and parse XML into dictionary"""
        self.counter = CtiOsCounter()
        xml = self.renderXML(ids_array)
        self.call_service(xml)
        dictionary = self.parseXML(self, xml, self.counter, self.logger)
        return dictionary

