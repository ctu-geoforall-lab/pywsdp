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
import os
import csv
import configparser
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
    def __init__(self, input_dictionary,logger):
        self.input_dictonary = input_dictionary
        self.logger = logger

    def _get_mapping_attributes_dir(self, csv_dir):
        """
        Args:
          csv_dir (str): Csv directory has to be absolute path, relative paths are not supported
        """
        if csv_dir and os.path.isabs(csv_dir):
            self.csv_dir = csv_dir
        else:
            # relative paths are not supported
            self.csv_dir = os.path.join(
                os.path.dirname(__file__)
            )

    def _read_mapping_attributes_dir(self, csv_name):
        """
        Read csv attributes as dictionary

        Args:
            csv_name (str): name of attribute mapping csv file

        Returns:
            dictionary (dict): (1.column:2.column)
        """
        dictionary = {}
        with open(os.path.join(self.mapping_attributes_dir, csv_name)) as csv_file:
            rows = csv.reader(csv_file, delimiter=';')
            for row in rows:
                [k, v, l] = row
                dictionary[k] = v
            return dictionary

    def _transform_names(xml_name):
        """
        Convert names in XML name to name in database (eg. StavDat to STAV_DAT)

        Args:
            xml_name (str): tag of xml attribute in xml response

        Returns:
            database_name (str): column names in database
        """

        database_name = re.sub('([A-Z]{1})', r'_\1', xml_name).upper()
        return database_name

    def _transform_names_dict(self, xml_name, config_file=None):
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
            # Read configuration
            self._config = configparser.ConfigParser()
            if config_file is None:
                config_file = os.path.join(os.path.abspath('ctios'), 'settings.ini')
            self._config.read(config_file)

            # Load dictionary with names of XML tags and their relevant database names
            self.mapping_attributes_dir = self._get_mapping_attributes_dir(self._config['files'].get('csv_dir'))
            mapping_attributes_dict = self._read_mapping_attributes_dir(self._config['files']['attribute_map_file'])
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
        for posident_id, posident_info in self.input_dictonary.items():
            #  Convert attributes
            for dat_name in posident_info:
                dat_name = self._transform_names(dat_name)
                if dat_name not in db_columns:
                    dat_name = self._transform_names_dict(dat_name)


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