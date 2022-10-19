"""
@package clients.helpers

@brief Helpers for CtiOS client

Classes:
 - helpers::XMLParser
 - helpers::Counter

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import xml.etree.ElementTree as et

from pywsdp.base.globalvars import xmlNamespace0, xmlNamespace1
from pywsdp.base.exceptions import WSDPResponseError


class XMLParser:
    """Class parsing ctiOS XML response into a dictionary."""

    def __call__(self, content, counter, logger):
        """
        Read content from XML and parses it.
        Raised:
            WSDPResponseError
        :param content: XML response (str)
        :param counter: counts posident errors (CtiOSCounter class)
        :param logger: logging class (Logger)
        :rtype: tuple (parsed XML attributes (nested dictonary), errors (dictionary))
        """
        root = et.fromstring(content)

        # Find tags with 'zprava' name
        xml_dict = {}
        xml_dict_errors = {}
        namespace_ns1 = xmlNamespace1["ctios"]
        os_tags = root.findall(".//{}zprava".format(namespace_ns1))
        for os_tag in os_tags:
            logger.info(" ")
            logger.info(os_tag.text)

        # Find all tags with 'os' name
        namespace_ns0 = xmlNamespace0["ctios"]
        namespace_length = len(namespace_ns0)
        for os_tag in root.findall(".//{}os".format(namespace_ns0)):

            # Save posident variable
            posident = os_tag.find("{}pOSIdent".format(namespace_ns0)).text

            if os_tag.find("{}chybaPOSIdent".format(namespace_ns0)) is not None:

                # Detect errors
                identifier = os_tag.find("{}chybaPOSIdent".format(namespace_ns0)).text

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
                xml_dict_errors[posident] = identifier
            else:
                # No errors detected
                xml_dict[posident] = {}
                counter.add_uspesne_stazeno()
                logger.info("POSIDENT {} USPESNE STAZEN".format(posident))

                # Create the dictionary with XML child attribute names and particular texts
                for child in os_tag.find(".//{}osDetail".format(namespace_ns0)):
                    # key: remove namespace from element name
                    name = child.tag
                    xml_dict[posident][name[namespace_length:]] = os_tag.find(
                        ".//{}".format(name)
                    ).text
                os_id = os_tag.find("{}osId".format(namespace_ns0)).text
                xml_dict[posident]["osId"] = os_id
        return xml_dict, xml_dict_errors


class Counter:
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
