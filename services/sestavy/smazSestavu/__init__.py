"""
@package pywsdp

@brief Base class creating the interface for SmazSestavu service

Classes:
 - smazSestavu::SmazSestavu

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import xml.etree.ElementTree as et

from base import WSDPBase
from base.logger import WSDPLogger
from base.exceptions import WSDPResponseError


class SmazSestavu(WSDPBase):
    """A concrete class that defines interface and main logic
    used for SeznamSestav service.
    """

    service_group = "sestavy"
    service_name = "smazSestavu"
    logger = WSDPLogger(service_name)

    def __init__(self, username, password, csv_path):
        super().__init__(username, password)
        self.csv_path = csv_path

    def parseXML(self, content):
        """Call generujCenoveUdajeParser XML parser
        Returns:
            xml_attributes (nested dictonary): parsed XML attributes
        """
        def get_xml_namespace_ns0():
            return "{http://katastr.cuzk.cz/sestavy/types/v2.9}"

        def get_xml_namespace_ns1():
            return "{http://katastr.cuzk.cz/commonTypes/v2.9}"

        root = et.fromstring(content)

        # Find tags with 'zprava' name
        namespace_ns1 = get_xml_namespace_ns1()
        os_tags = root.findall(".//{}zprava".format(namespace_ns1))
        for os_tag in os_tags:
            self.logger.info(os_tag.text)

        # Find all tags with 'report' name
        xml_dict = {}
        namespace_ns0 = get_xml_namespace_ns0()
        for os_tag in root.findall(".//{}report".format(namespace_ns0)):

            # Id sestavy
            xml_dict["idSestavy"] = os_tag.find("{}id".format(namespace_ns0)).text
            if xml_dict["idSestavy"]:
                self.logger.info("ID sestavy: {}".format(xml_dict["idSestavy"]))
            else:
                raise WSDPResponseError(
                    self.logger,
                    "ID sestavy nebylo vraceno")

            # Nazev sestavy
            if os_tag.find("{}nazev".format(namespace_ns0)) is not None:
                xml_dict["nazev"] = os_tag.find("{}nazev".format(namespace_ns0)).text
                self.logger.info("Nazev sestavy: {}".format(xml_dict["nazev"]))

            # Pocet jednotek
            if os_tag.find("{}pocetJednotek".format(namespace_ns0)) is not None:
                xml_dict["pocetJednotek"] = os_tag.find("{}pocetJednotek".format(namespace_ns0)).text
                self.logger.info("Pocet jednotek: {}".format(xml_dict["pocetJednotek"]))

            # Pocet stran
            if os_tag.find("{}pocetStran".format(namespace_ns0)) is not None:
                xml_dict["pocetStran"] = os_tag.find("{}pocetStran".format(namespace_ns0)).text
                self.logger.info("Pocet stran: {}".format(xml_dict["pocetStran"]))

            # Cena
            if os_tag.find("{}cena".format(namespace_ns0)) is not None:
                xml_dict["cena"] = os_tag.find("{}cena".format(namespace_ns0)).text
                self.logger.info("Cena: {}".format(xml_dict["cena"]))

            # Datum pozadavku
            if os_tag.find("{}datumPozadavku".format(namespace_ns0)) is not None:
                xml_dict["datumPozadavku"] = os_tag.find("{}datumPozadavku".format(namespace_ns0)).text
                self.logger.info("Datum pozadavku: {}".format(xml_dict["datumPozadavku"]))

            # Datum spusteni
            if os_tag.find("{}datumSpusteni".format(namespace_ns0)) is not None:
                xml_dict["datumSpusteni"] = os_tag.find("{}datumSpusteni".format(namespace_ns0)).text
                self.logger.info("Datum spusteni: {}".format(xml_dict["datumSpusteni"]))

            # Datum vytvoreni
            if os_tag.find("{}datumVytvoreni".format(namespace_ns0))is not None:
                xml_dict["datumVytvoreni"] = os_tag.find("{}datumVytvoreni".format(namespace_ns0)).text
                self.logger.info("Datum vytvoreni: {}".format(xml_dict["datumVytvoreni"]))

            # Stav sestavy
            if os_tag.find("{}stav".format(namespace_ns0)) is not None:
                xml_dict["stav"] = os_tag.find("{}stav".format(namespace_ns0)).text
                self.logger.info("Stav sestavy: {}".format(xml_dict["stav"]))

            # Format
            if os_tag.find("{}format".format(namespace_ns0)) is not None:
                xml_dict["format"] = os_tag.find("{}format".format(namespace_ns0)).text
                self.logger.info("Format sestavy: {}".format(xml_dict["format"]))

            # Elektronicka znacka
            if os_tag.find("{}elZnacka".format(namespace_ns0)) is not None:
                xml_dict["elZnacka"] = os_tag.find("{}elZnacka".format(namespace_ns0)).text
                self.logger.info("Elektronicka znacka: {}".format(xml_dict["elZnacka"]))

            # Soubor sestavy
            if os_tag.find("{}souborSestavy".format(namespace_ns0)) is not None:
                xml_dict["souborSestavy"] = os_tag.find("{}souborSestavy".format(namespace_ns0)).text

        return xml_dict

    def get_parameters_from_txt(self, txt_path):
        """Get parameters array from text file (delimiter is ',')."""
        parameters_array = []
        with open(txt_path) as f:
            for line in f:
                key, value = line.split()
                row = "<v2:{0}>{1}</v2:{0}>".format(key, value)
                parameters_array.append(row)
        return parameters_array

    def get_parameters_from_dict(self, dictionary):
        """Get parameters array from text file (delimiter is ',')."""
        parameters_array = []
        for key, value in dictionary.items():
            row = "<v2:{0}>{1}</v2:{0}>".format(key, value)
            parameters_array.append(row)
        return parameters_array

    def process(self, parameters_array):
        """Main wrapping method"""
        xml = self.renderXML(parameters="".join(parameters_array))
        response_xml = self.call_service(xml)
        xml_dict = self.parseXML(response_xml)
        return xml_dict
