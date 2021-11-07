"""
@package pywsdp

@brief Base class creating the interface for Sestavy service

Classes:
 - base::SestavyBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os
import configparser

from base import WSDPBase
from base.logger import WSDPLogger
from base.exceptions import WSDPResponseError
from services.sestavy.helpers import SestavyXMLParser


class SestavyBase(WSDPBase):
    """A concrete class that defines interface and main logic
    used for VratSestavu service.
    """
    service_group = "sestavy"

    def __init__(self, username, password):
        super().__init__(username, password)

    def get_service_path(self):
        """Method for getting absolute service path"""
        raise NotImplementedError

    @property
    def service_name(self):
        """A type of service - ctiOS, sestavy, vyhledat, ciselniky etc."""
        return self.service_name

    def parseXML(self, content):
        """Call ctiOS XML parser"""
        return SestavyXMLParser()(
            content=content, logger=self.logger
        )

    def get_listina_id(self):
        """Main wrapping method"""
        return "<v2:{0}>{1}</v2:{0}>".format("idSestavy", self.xml_dict["idSestavy"])

    def get_format(self):
        """Main wrapping method"""
        return self.xml_dict["format"]

    def get_soubor_sestavy(self):
        """Main wrapping method"""
        return self.xml_dict["souborSestavy"]

    def zpracujSestavu(self):
        self.service_name = "seznamSestav"
        self._process()

    def zauctujSestavu(self):
        self.service_name = "vratSestavu"
        self._process()

    def smazSestavu(self):
        self.service_name = "smazSestavu"
        self._process()
        self.not_deleted = False

    def _process(self):
        """Main wrapping method"""
        # Read configuration from config file
        self.service_path = self.get_service_path()
        self.config_path = self.get_config_path()
        self._config = configparser.ConfigParser()
        self._config.read(self.config_path)
        # Set headers
        self.get_service_headers()
        self.template_path = self.get_template_path()
        self.parameters = self.get_listina_id()
        xml = self.renderXML(parameters="".join(self.parameters))
        response_xml = self.call_service(xml)
        self.xml_dict = self.parseXML(response_xml)

    def __del__(self):
        if self.not_deleted:
            self.smazSestavu()