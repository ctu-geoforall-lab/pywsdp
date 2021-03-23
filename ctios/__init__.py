###############################################################################
# Name:         library CTI_OS
# Purpose:      Sends a request to CTI_OS service based on given posident array
#               and stores response to SQLITE DB
# Date:         May 2021
# Author:       Linda Kladivova
# Email:        l.kladivova@seznam.cz
###############################################################################

import os
import configparser

from templates import Templates
from ctios.csv import CtiOsCsv
from ctios.db import CtiOsDb
from ctios.parser import CtiOsParser
from ctios.stats import CtiOsStats
from ctios.converter import CtiOsConverter
from wsdp import WSDPBase


class CtiOs(WSDPBase):
    """
        CTIOS class contains methods for requesting CTIOS service, processing the response and saving it to db
    """

    def __init__(self, username, password, db_dir, sql=None, log_dir=None, config_file=None, csv_dir=None):
        """
        Constructor of CTIOS class

        Args:
            username (str): Username for CTIOS service
            password (str): Password for CTIOS service
            db_dir (str): Path to database
            sql (str): sql select for selecting pseudo ids
            log_dir (str): Path to log file
            config_file (str): Configuration file (not mandatory, if not specified, default config file is selected)
            output (str): The place where processed attributes should be stored - supported db or csv
        """
        # CTI_OS authentication
        self._username = username
        self._password = password

        # Database schema and sql select for selecting pseudo ids
        self.schema = "OPSUB"
        if sql:
            self.sql = sql

        # Connection to db
        self.db = CtiOsDb(db_dir)

        # Stats
        self.stats = CtiOsStats()

        # Read configuration
        self._config = configparser.ConfigParser()
        if config_file is None:
            config_file = os.path.join(os.path.abspath('ctios'), 'settings.ini')
        self._config.read(config_file)

    def define_log_name(self):
        """Method for defining logger name according to service"""
        return "pyctios"

    def define_service_headers(self):
        """
        Define service headers needed for calling CtiOs service
        Returns:
            service headers (dictionary):  parameters for calling CtiOs service
        """
        # CTIOS service parameters loaded from ini file
        service_headers = {}
        service_headers['content_type'] = self._config['service headers']['content_type']
        service_headers['accept_encoding'] = self._config['service headers']['accept_encoding']
        service_headers['soap_action'] = self._config['service headers']['soap_action']
        service_headers['connection'] = self._config['service headers']['connection']
        service_headers['endpoint'] = self._config['service headers']['endpoint']
        return service_headers

    def draw_up_xml_request(self, sql):
        """
        Draw up xml request using ids array and function for rendering from CtiOsTemplate class

        Args:
            ids (list): pseudo ids from db

        Returns:
            request_xml (str): xml request for CtiOS service
        """
        ids = self.db.get_ids_from_db("OPSUB")
        ids_array = []

        for i in ids:
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i[0])
            ids_array.append(row)  # Add all tags to one list

        # Render XML request using request xml template
        request_xml = Templates(self._config['files'].get('template_dir')).render(
            self._config['files']['request_xml_file'], username=self._username, password=self._password,
            posidents=''.join(ids_array)
        )
        return request_xml

    def create_parser(self, namespace, content):
        """Call CtiOs XML parser"""
        return CtiOsParser(content=content,
                           namespace=self._config['other parameters']['namespace'],
                           stats=self.stats,
                           logger=self.logger)

    def create_output(self, csv_dir):
        """Creating the final output - must be redefined in subclass"""
        # If required, output to csv
        if os.path.exists(csv_dir):
            output_csv = CtiOsCsv(csv_dir)
            output_csv.write_dictionary_to_csv(self.dictionary)
        # Output to db
        self.db.add_column_to_db(self.schema, "OS_ID", "text")
        columns = self.db.get_columns_names(self.schema)
        self.dictionary = CtiOsConverter(self.dictionary).convert_attributes(columns)
        self.db.save_attributes_to_db(self.schema, self.dictionary)