###############################################################################
# Name:         CtiOSConvertor
# Purpose:      Class for converting XML attribute names to DB attribute names
# Date:         March 2021
# Copyright:    (C) 2021 Linda Kladivova
# Email:        l.kladivova@seznam.cz
###############################################################################

import re
import os
import configparser

from ctios.exceptions import CtiOsError
from ctios.csv import CtiOsCsv


class CtiOsConverter:
    """
    CTIOS class which convert input dictionary to CtiOs db dictionary
    """
    def __init__(self, input_dictionary):
        self.input_dictonary = input_dictionary

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
            dictionary = CtiOsCsv(self._config['files'].get('csv_dir')).read_csv_as_dictionary(
                self._config['files']['attribute_map_file']
            )
            database_name = dictionary[xml_name]
            return database_name

        except Exception as e:
            raise CtiOsError("XML ATTRIBUTE NAME CANNOT BE CONVERTED TO DATABASE COLUMN NAME: {}".format(e))

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