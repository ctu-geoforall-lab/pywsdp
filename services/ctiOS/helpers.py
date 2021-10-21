"""
@package ctiOS.helpers

@brief Base script for general classes needed for ctiOS service

Classes:
 - ctiOS::CtiOSXMLParser
 - ctiOS::CtiOSCounter


(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""


import xml.etree.ElementTree as et

from base.exceptions import WSDPResponseError


class CtiOSXMLParser:
    """Class parsing ctiOS XML response into a dictionary"""

    def __call__(self, content, counter, logger):
        """
        Read content from XML and parses it

        Args:
            content (str): content of XML response
            counter (class): counts posident errors
            logger (class): log class
        Returns:
            xml_attributes (nested dictonary): parsed XML attributes
        """
        root = et.fromstring(content)
        namespace = self._get_xml_namespace()
        namespace_length = len(namespace)
        xml_dict = {}

        # Find all tags with 'os' name
        for os_tag in root.findall(".//{}os".format(namespace)):

            # Save posident variable
            posident = os_tag.find("{}pOSIdent".format(namespace)).text

            if os_tag.find("{}chybaPOSIdent".format(namespace)) is not None:

                # Errors detected
                identifier = os_tag.find("{}chybaPOSIdent".format(namespace)).text

                if identifier == "NEPLATNY_IDENTIFIKATOR":
                    counter.add_neplatny_identifikator()
                elif identifier == "EXPIROVANY_IDENTIFIKATOR":
                    counter.add_expirovany_identifikator()
                elif identifier == "OPRAVNENY_SUBJEKT_NEEXISTUJE":
                    counter.add_opravneny_subjekt_neexistuje()

                # Write to log
                if identifier in (
                    "NEPLATNY_IDENTIFIKATOR",
                    "EXPIROVANY_IDENTIFIKATOR",
                    "OPRAVNENY_SUBJEKT_NEEXISTUJE",
                ):
                    logger.info(
                        "POSIDENT {} {}".format(posident, identifier.replace("_", " "))
                    )
                else:
                    raise WSDPResponseError(
                        logger,
                        "POSIDENT {} {}".format(posident, identifier.replace("_", " ")),
                    )
            else:
                # No errors detected
                xml_dict[posident] = {}
                counter.add_uspesne_stazeno()
                logger.info("POSIDENT {} USPESNE STAZEN".format(posident))

                # Create the dictionary with XML child attribute names and particular texts
                for child in os_tag.find(".//{}osDetail".format(namespace)):
                    # key: remove namespace from element name
                    name = child.tag
                    xml_dict[posident][name[namespace_length:]] = os_tag.find(
                        ".//{}".format(name)
                    ).text
                os_id = os_tag.find("{}osId".format(namespace)).text
                xml_dict[posident]["osId"] = os_id
        return xml_dict

    def _get_xml_namespace(self):
        return "{http://katastr.cuzk.cz/ctios/types/v2.8}"


class CtiOSCounter:
    """
    CtiOS class which counts posident stats
    """

    def __init__(self):
        self.neplatny_identifikator = 0
        self.expirovany_identifikator = 0
        self.opravneny_subjekt_neexistuje = 0
        self.uspesne_stazeno = 0

    def add_neplatny_identifikator(self):
        self.neplatny_identifikator += 1

    def add_expirovany_identifikator(self):
        self.expirovany_identifikator += 1

    def add_opravneny_subjekt_neexistuje(self):
        self.opravneny_subjekt_neexistuje += 1

    def add_uspesne_stazeno(self):
        self.uspesne_stazeno += 1
