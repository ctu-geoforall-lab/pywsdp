"""
@package ctios.helpers

@brief Base script for general classes needed for CtiOs service

Classes:
 - base::CtiOsXMLParser
 - base::CtiOsConverter
 - base::CtiOsCounter


(C) 2021 Linda Kladivova l.kladivova@seznam.cz
This library is free under the GNU General Public License.
"""

import re
import csv
import xml.etree.ElementTree as et

from ctios.exceptions import CtiOsError, CtiOsResponseError



class CtiOsXMLParser():
    """Class parsing CtiOs Xml response into a dictionary"""
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
        for os_tag in root.findall('.//{}os'.format(namespace)):

            # Save posident variable
            posident = os_tag.find('{}pOSIdent'.format(namespace)).text
            xml_dict[posident] = {}

            if os_tag.find('{}chybaPOSIdent'.format(namespace)) is not None:

                # Errors detected
                identifier = os_tag.find('{}chybaPOSIdent'.format(namespace)).text

                if identifier == "NEPLATNY_IDENTIFIKATOR":
                    counter.add_neplatny_identifikator()
                elif identifier == "EXPIROVANY_IDENTIFIKATOR":
                    counter.add_expirovany_identifikator()
                elif identifier == "OPRAVNENY_SUBJEKT_NEEXISTUJE":
                    counter.add_opravneny_subjekt_neexistuje()
                else:
                    raise CtiOsResponseError(logger, 'POSIDENT {} {}'.format(posident, identifier.replace('_', ' ')))
            else:
                # No errors detected
                # Create the dictionary with XML child attribute names and particular texts
                for child in os_tag.find('.//{}osDetail'.format(namespace)):
                    # key: remove namespace from element name
                    name = child.tag
                    xml_dict[posident][name[namespace_length:]] = os_tag.find('.//{}'.format(name)).text

        return xml_dict

    def _get_xml_namespace(self):
        return '{http://katastr.cuzk.cz/ctios/types/v2.8}'


class CtiOsConverter():
    """
    CTIOS class for converting XML attribute names to DB attribute names
    """
    def __init__(self, input_dictionary, mapping_attributes_path, logger):
        self.input_dictionary = input_dictionary
        self.logger = logger
        self.mapping_attributes_path = mapping_attributes_path

    def _read_mapping_attributes_dir(self):
        """
        Read csv attributes as dictionary

        Args:
            csv_name (str): name of attribute mapping csv file

        Returns:
            dictionary (dict): (1.column:2.column)
        """
        dictionary = {}
        with open(self.mapping_attributes_path) as csv_file:
            rows = csv.reader(csv_file, delimiter=';')
            for row in rows:
                [k, v, l] = row
                dictionary[k] = v
        return dictionary

    def _transform_names(self, xml_name):
        """
        Convert names in XML name to name in database (eg. StavDat to STAV_DAT)

        Args:
            xml_name (str): tag of xml attribute in xml response

        Returns:
            database_name (str): column names in database
        """

        database_name = re.sub('([A-Z]{1})', r'_\1', xml_name).upper()
        return database_name

    def _transform_names_dict(self, xml_name):
        """
        Convert names in XML name to name in database based on special dictionary

        Args:
            xml_name (str): tag of xml attribute in xml response
            config_file (str): configuration file (not mandatory)

        Raises:
            CtiOsError(XML ATTRIBUTE NAME CANNOT BE CONVERTED TO DATABASE COLUMN NAME)

        Returns:
            database_name (str): column names in database
        """
        try:
            # Load dictionary with names of XML tags and their relevant database names
            mapping_attributes_dict = self._read_mapping_attributes_dir()
            database_name = mapping_attributes_dict[xml_name]
            return database_name

        except Exception as e:
            raise CtiOsError(self.logger, "XML ATTRIBUTE NAME CANNOT BE CONVERTED TO DATABASE COLUMN NAME: {}".format(e))

    def convert_attributes(self, db_columns):
        """
        Convert XML attribute names to db attributes names

        Args:
            dictionary (nested dictonary): original XML attributes

        Returns:
            dictionary (nested dictonary): converted DB attributes
        """
        for posident_id, posident_info in self.input_dictionary.items():
            #  Convert attributes
            for xml_name in posident_info:
                dat_name = self._transform_names(xml_name)
                if dat_name not in db_columns:
                    dat_name = self._transform_names_dict(xml_name)


class CtiOsCounter():
    """
    CTIOS class which counts posident stats
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