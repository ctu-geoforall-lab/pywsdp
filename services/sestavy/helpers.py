"""
@brief Base script for general classes needed for Sestavy

Classes:
 - sestavy::SestavyXMLParser


(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""


import xml.etree.ElementTree as et

from base.exceptions import WSDPResponseError


class SestavyXMLParser:
    """Class parsing sestavy XML response into a dictionary"""

    def __call__(self, content, logger):
        """
        Read content from XML and parses it

        Args:
            content (str): content of XML response
            logger (class): log class
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
            logger.info(os_tag.text)

        # Find all tags with 'report' name
        xml_dict = {}
        namespace_ns0 = get_xml_namespace_ns0()
        for os_tag in root.findall(".//{}report".format(namespace_ns0)):

            # Id sestavy
            xml_dict["idSestavy"] = os_tag.find("{}id".format(namespace_ns0)).text
            if xml_dict["idSestavy"]:
                logger.info("ID sestavy: {}".format(xml_dict["idSestavy"]))
            else:
                raise WSDPResponseError(
                    logger,
                    "ID sestavy nebylo vraceno")

            # Nazev sestavy
            if os_tag.find("{}nazev".format(namespace_ns0)) is not None:
                xml_dict["nazev"] = os_tag.find("{}nazev".format(namespace_ns0)).text
                logger.info("Nazev sestavy: {}".format(xml_dict["nazev"]))

            # Pocet jednotek
            if os_tag.find("{}pocetJednotek".format(namespace_ns0)) is not None:
                xml_dict["pocetJednotek"] = os_tag.find("{}pocetJednotek".format(namespace_ns0)).text
                logger.info("Pocet jednotek: {}".format(xml_dict["pocetJednotek"]))

            # Pocet stran
            if os_tag.find("{}pocetStran".format(namespace_ns0)) is not None:
                xml_dict["pocetStran"] = os_tag.find("{}pocetStran".format(namespace_ns0)).text
                logger.info("Pocet stran: {}".format(xml_dict["pocetStran"]))

            # Cena
            if os_tag.find("{}cena".format(namespace_ns0)) is not None:
                xml_dict["cena"] = os_tag.find("{}cena".format(namespace_ns0)).text
                logger.info("Cena: {}".format(xml_dict["cena"]))

            # Datum pozadavku
            if os_tag.find("{}datumPozadavku".format(namespace_ns0)) is not None:
                xml_dict["datumPozadavku"] = os_tag.find("{}datumPozadavku".format(namespace_ns0)).text
                logger.info("Datum pozadavku: {}".format(xml_dict["datumPozadavku"]))

            # Datum spusteni
            if os_tag.find("{}datumSpusteni".format(namespace_ns0)) is not None:
                xml_dict["datumSpusteni"] = os_tag.find("{}datumSpusteni".format(namespace_ns0)).text
                logger.info("Datum spusteni: {}".format(xml_dict["datumSpusteni"]))

            # Datum vytvoreni
            if os_tag.find("{}datumVytvoreni".format(namespace_ns0))is not None:
                xml_dict["datumVytvoreni"] = os_tag.find("{}datumVytvoreni".format(namespace_ns0)).text
                logger.info("Datum vytvoreni: {}".format(xml_dict["datumVytvoreni"]))

            # Stav sestavy
            if os_tag.find("{}stav".format(namespace_ns0)) is not None:
                xml_dict["stav"] = os_tag.find("{}stav".format(namespace_ns0)).text
                logger.info("Stav sestavy: {}".format(xml_dict["stav"]))

            # Format
            if os_tag.find("{}format".format(namespace_ns0)) is not None:
                xml_dict["format"] = os_tag.find("{}format".format(namespace_ns0)).text
                logger.info("Format sestavy: {}".format(xml_dict["format"]))

            # Elektronicka znacka
            if os_tag.find("{}elZnacka".format(namespace_ns0)) is not None:
                xml_dict["elZnacka"] = os_tag.find("{}elZnacka".format(namespace_ns0)).text
                logger.info("Elektronicka znacka: {}".format(xml_dict["elZnacka"]))

            # Soubor sestavy
            if os_tag.find("{}souborSestavy".format(namespace_ns0)) is not None:
                xml_dict["souborSestavy"] = os_tag.find("{}souborSestavy".format(namespace_ns0)).text

        return xml_dict