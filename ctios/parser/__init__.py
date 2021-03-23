###############################################################################
# Name:         CtiOSParser
# Purpose:      Parses CtiOs XML response
# Date:         March 2021
# Copyright:    (C) 2021 Linda Kladivova
# Email:        l.kladivova@seznam.cz
###############################################################################

import xml.etree.ElementTree as et

from ctios.exceptions import CtiOsError
from wsdp.logger import Logger


class CtiOsResponseError(CtiOsError):
    """Basic exception for errors raised by error in response"""
    def __init__(self, msg):
        super(CtiOsResponseError, self).__init__('{} - {}'.format('XML response ERROR', msg))


class CtiOsParser():

    def __call__(self, content, namespace, stats, logger=None):
        """
        Read content from XML and parses it

        Args:
            content (str): content of XML file

        Returns:
            xml_attributes (nested dictonary): parsed XML attributes
        """
        root = et.fromstring(content)
        namespace_length = len(namespace)
        xml_dict = {}

        # Find all tags with 'os' name
        for os in root.findall('.//{}os'.format(namespace)):

            xml_dict[os] = {}

            # Save posident variable
            posident = os.find('{}pOSIdent'.format(namespace)).text

            if os.find('{}chybaPOSIdent'.format(namespace)) is not None:

                # Errors detected
                identifier = os.find('{}chybaPOSIdent'.format(namespace)).text

                if identifier == "NEPLATNY_IDENTIFIKATOR":
                    stats.add_neplatny_identifikator()
                elif identifier == "EXPIROVANY_IDENTIFIKATOR":
                    stats.add_expirovany_identifikator()
                elif identifier == "OPRAVNENY_SUBJEKT_NEEXISTUJE":
                    stats.add_opravneny_subjekt_neexistuje()
                else:
                    raise CtiOsResponseError('Unknown chybaPOSIdent')
                if logger:
                    logger.error('POSIDENT {} {}'.format(posident, identifier.replace('_', ' ')))
            else:
                # No errors detected
                # Create the dictionary with XML child attribute names and particular texts
                for child in os.find('.//{}osDetail'.format(namespace)):
                    # key: remove namespace from element name
                    name = child.tag
                    xml_dict[os][name[namespace_length:]] = os.find('.//{}'.format(name)).text
        return xml_dict