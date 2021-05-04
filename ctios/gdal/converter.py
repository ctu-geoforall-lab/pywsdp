"""
@package ctios.helpers

@brief Base script for general classes needed for CtiOs service

Classes:
 - gdal::Xml2DbConverter


(C) 2021 Linda Kladivova l.kladivova@seznam.cz
This library is free under the GNU General Public License.
"""

import re
import csv

from ctios.exceptions import CtiOsError



class Xml2DbConverter():
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